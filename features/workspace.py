from database.db_manager import DatabaseManager

class WorkspaceManager:
    """Workspace service to integrate project management"""

    @staticmethod
    def create_workspace(application_id, job_id, freelancer_id, client_id):
        """Auto-create project workspace when application is accepted"""
        with DatabaseManager.get_cursor() as cursor:
            # Create project workspace
            query = """INSERT INTO projects (job_id, freelancer_id, client_id, status, progress_percentage)
                       VALUES (%s, %s, %s, 'active', 0)"""
            cursor.execute(query, (job_id, freelancer_id, client_id))
            project_id = cursor.lastrowid

            # Create default milestones
            default_milestones = [
                ('Initial Design', 'Design phase and planning', 1),
                ('Development', 'Core development work', 2),
                ('Testing', 'Testing and quality assurance', 3),
                ('Final Delivery', 'Final deliverable submission', 4)
            ]

            for milestone_name, description, order_number in default_milestones:
                milestone_query = """INSERT INTO milestones (project_id, milestone_name, description, status, order_number)
                                    VALUES (%s, %s, %s, 'pending', %s)"""
                cursor.execute(milestone_query, (project_id, milestone_name, description, order_number))

            # Log workspace creation
            WorkspaceManager.log_activity(
                project_id,
                freelancer_id,
                'workspace_created',
                f'Workspace created for application #{application_id}'
            )

            return project_id

    @staticmethod
    def get_workspace(project_id):
        """Get workspace details by project ID"""
        with DatabaseManager.get_cursor() as cursor:
            # Get project details
            cursor.execute("""
                SELECT p.*, j.title as job_title, j.description as job_description,
                       j.budget_min, j.budget_max, j.deadline,
                       f.name as freelancer_name, f.email as freelancer_email,
                       c.name as client_name, c.email as client_email
                FROM projects p
                JOIN jobs j ON p.job_id = j.job_id
                JOIN users f ON p.freelancer_id = f.user_id
                JOIN users c ON p.client_id = c.user_id
                WHERE p.project_id = %s
            """, (project_id,))
            project = cursor.fetchone()

            if not project:
                return None

            # Get milestones
            cursor.execute("""
                SELECT * FROM milestones
                WHERE project_id = %s
                ORDER BY order_number
            """, (project_id,))
            milestones = cursor.fetchall()

            return {
                'project': project,
                'milestones': milestones
            }

    @staticmethod
    def get_freelancer_workspaces(freelancer_id):
        """Get all active workspaces for a freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.*, j.title as job_title, c.name as client_name
                FROM projects p
                JOIN jobs j ON p.job_id = j.job_id
                JOIN users c ON p.client_id = c.user_id
                WHERE p.freelancer_id = %s AND p.status = 'active'
                ORDER BY p.created_at DESC
            """, (freelancer_id,))
            return cursor.fetchall()

    @staticmethod
    def get_client_workspaces(client_id):
        """Get all workspaces for a client"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.*, j.title as job_title, f.name as freelancer_name
                FROM projects p
                JOIN jobs j ON p.job_id = j.job_id
                JOIN users f ON p.freelancer_id = f.user_id
                WHERE p.client_id = %s
                ORDER BY p.created_at DESC
            """, (client_id,))
            return cursor.fetchall()

    @staticmethod
    def submit_deliverable(milestone_id, freelancer_id, file_path=None, description=None):
        """Submit a deliverable to a milestone with version tracking"""
        with DatabaseManager.get_cursor() as cursor:
            # Get current version number for this milestone
            cursor.execute("""
                SELECT COALESCE(MAX(version_number), 0) as max_version
                FROM submissions
                WHERE milestone_id = %s
            """, (milestone_id,))
            result = cursor.fetchone()
            next_version = result['max_version'] + 1

            # Insert submission
            query = """INSERT INTO submissions (milestone_id, deliverable_description, file_path, version_number)
                       VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (milestone_id, description, file_path, next_version))
            submission_id = cursor.lastrowid

            # Get project_id for activity log
            cursor.execute("SELECT project_id FROM milestones WHERE milestone_id = %s", (milestone_id,))
            project = cursor.fetchone()
            project_id = project['project_id']

            # Log activity
            WorkspaceManager.log_activity(
                project_id,
                freelancer_id,
                'deliverable_submitted',
                f'Deliverable v{next_version} submitted for milestone #{milestone_id}'
            )

            return submission_id

    @staticmethod
    def get_milestone_submissions(milestone_id):
        """Get all submissions for a milestone with version history"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM submissions
                WHERE milestone_id = %s
                ORDER BY version_number DESC
            """, (milestone_id,))
            return cursor.fetchall()

    @staticmethod
    def approve_milestone(milestone_id, client_id, feedback=None):
        """Client approves a milestone"""
        with DatabaseManager.get_cursor() as cursor:
            # Update milestone status
            cursor.execute("""
                UPDATE milestones
                SET status = 'approved'
                WHERE milestone_id = %s
            """, (milestone_id,))

            # Add feedback to latest submission if provided
            if feedback:
                cursor.execute("""
                    UPDATE submissions
                    SET client_feedback = %s
                    WHERE milestone_id = %s
                    ORDER BY version_number DESC
                    LIMIT 1
                """, (feedback, milestone_id))

            # Get project_id
            cursor.execute("SELECT project_id FROM milestones WHERE milestone_id = %s", (milestone_id,))
            project = cursor.fetchone()
            project_id = project['project_id']

            # Update progress percentage
            WorkspaceManager.update_progress(project_id)

            # Log activity
            WorkspaceManager.log_activity(
                project_id,
                client_id,
                'milestone_approved',
                f'Milestone #{milestone_id} approved'
            )

            return True

    @staticmethod
    def request_revision(milestone_id, client_id, feedback):
        """Client requests revision on a milestone"""
        with DatabaseManager.get_cursor() as cursor:
            # Update milestone status
            cursor.execute("""
                UPDATE milestones
                SET status = 'revision_requested'
                WHERE milestone_id = %s
            """, (milestone_id,))

            # Add feedback to latest submission
            cursor.execute("""
                UPDATE submissions
                SET client_feedback = %s
                WHERE milestone_id = %s
                ORDER BY version_number DESC
                LIMIT 1
            """, (feedback, milestone_id))

            # Get project_id
            cursor.execute("SELECT project_id FROM milestones WHERE milestone_id = %s", (milestone_id,))
            project = cursor.fetchone()
            project_id = project['project_id']

            # Log activity
            WorkspaceManager.log_activity(
                project_id,
                client_id,
                'revision_requested',
                f'Revision requested for milestone #{milestone_id}'
            )

            return True

    @staticmethod
    def update_progress(project_id):
        """Calculate and update progress percentage based on completed milestones"""
        with DatabaseManager.get_cursor() as cursor:
            # Count total and approved milestones
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved
                FROM milestones
                WHERE project_id = %s
            """, (project_id,))
            result = cursor.fetchone()

            total = result['total']
            approved = result['approved']

            progress = int((approved / total * 100)) if total > 0 else 0

            # Update project progress
            cursor.execute("""
                UPDATE projects
                SET progress_percentage = %s
                WHERE project_id = %s
            """, (progress, project_id))

            # If all milestones approved, mark project as completed
            if progress == 100:
                cursor.execute("""
                    UPDATE projects
                    SET status = 'completed', completed_at = NOW()
                    WHERE project_id = %s
                """, (project_id,))

            return progress

    @staticmethod
    def get_activity_log(project_id):
        """Get activity log for a workspace"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as user_name
                FROM activity_log a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.project_id = %s
                ORDER BY a.created_at DESC
            """, (project_id,))
            return cursor.fetchall()

    @staticmethod
    def log_activity(project_id, user_id, activity_type, description):
        """Log an activity in the workspace"""
        with DatabaseManager.get_cursor() as cursor:
            query = """INSERT INTO activity_log (project_id, user_id, activity_type, description)
                       VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (project_id, user_id, activity_type, description))
            return cursor.lastrowid

    @staticmethod
    def mark_disputed(project_id, user_id, reason):
        """Mark a project as disputed"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                UPDATE projects
                SET status = 'disputed'
                WHERE project_id = %s
            """, (project_id,))

            WorkspaceManager.log_activity(
                project_id,
                user_id,
                'project_disputed',
                f'Project marked as disputed: {reason}'
            )

            return True
