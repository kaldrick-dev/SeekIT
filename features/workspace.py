from database.db_manager import DatabaseManager
from utils.display import Display

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

    @staticmethod
    def display_workspaces(user_id, user_type):
        """Display all workspaces for a user"""
        if user_type == 'freelancer':
            workspaces = WorkspaceManager.get_freelancer_workspaces(user_id)
            Display.print_header("MY ACTIVE PROJECTS")
        else:
            workspaces = WorkspaceManager.get_client_workspaces(user_id)
            Display.print_header("MY CLIENT PROJECTS")

        if not workspaces:
            Display.print_warning("No active projects found")
            return

        for workspace in workspaces:
            WorkspaceManager.print_workspace_card(workspace, user_type)

    @staticmethod
    def print_workspace_card(workspace, user_type):
        """Print a formatted workspace card"""
        project_id = workspace.get('project_id', 'N/A')
        job_title = workspace.get('job_title', 'Untitled Project')
        status = workspace.get('status', 'unknown')
        progress = workspace.get('progress_percentage', 0)
        created_at = workspace.get('created_at', 'N/A')

        if user_type == 'freelancer':
            partner_name = workspace.get('client_name', 'N/A')
            partner_label = 'Client'
        else:
            partner_name = workspace.get('freelancer_name', 'N/A')
            partner_label = 'Freelancer'

        print("\n" + "+" + "-" * 78 + "+")
        print(f"| {Display.color_text(f'Project #{project_id}: {job_title}', 'cyan', bold=True):<87}|")
        print("+" + "-" * 78 + "+")
        print(f"| {Display.color_text(partner_label + ':', 'yellow')} {partner_name}".ljust(87) + "|")
        print(f"| {Display.color_text('Status:', 'yellow')} {Display._get_status_text(status)}".ljust(100) + "|")
        print(f"| {Display.color_text('Progress:', 'yellow')} {progress}%".ljust(87) + "|")
        print(f"| {Display.color_text('Created:', 'yellow')} {created_at}".ljust(87) + "|")
        print("+" + "-" * 78 + "+\n")

    @staticmethod
    def display_workspace_details(project_id):
        """Display detailed workspace information"""
        workspace = WorkspaceManager.get_workspace(project_id)

        if not workspace:
            Display.print_error("Workspace not found")
            return

        project = workspace['project']
        milestones = workspace['milestones']

        Display.print_header(f"PROJECT: {project.get('job_title', 'Untitled')}")

        # Project info
        Display.print_subheader("Project Information")
        print(f"  {Display.color_text('Project ID:', 'cyan')} {project.get('project_id')}")
        print(f"  {Display.color_text('Freelancer:', 'cyan')} {project.get('freelancer_name')} ({project.get('freelancer_email')})")
        print(f"  {Display.color_text('Client:', 'cyan')} {project.get('client_name')} ({project.get('client_email')})")
        print(f"  {Display.color_text('Status:', 'cyan')} {Display._get_status_text(project.get('status'))}")
        print(f"  {Display.color_text('Progress:', 'cyan')} {project.get('progress_percentage', 0)}%")
        print()

        # Milestones
        Display.print_subheader("Milestones")
        if milestones:
            for milestone in milestones:
                status_color = 'green' if milestone['status'] == 'approved' else 'yellow'
                print(f"  {milestone['order_number']}. {Display.color_text(milestone['milestone_name'], 'white', bold=True)}")
                print(f"     Status: {Display.color_text(milestone['status'].upper(), status_color)}")
                print(f"     {milestone['description']}")
                print()
        else:
            Display.print_warning("No milestones defined")

    @staticmethod
    def submit_deliverable_flow(user_id):
        """Interactive flow for freelancers to submit deliverables"""
        Display.print_header("SUBMIT DELIVERABLE")

        # Get freelancer's active projects
        workspaces = WorkspaceManager.get_freelancer_workspaces(user_id)

        if not workspaces:
            Display.print_warning("You have no active projects")
            return

        # Display projects
        print("Your active projects:")
        for idx, workspace in enumerate(workspaces, start=1):
            print(f"  [{idx}] {workspace['job_title']} (Project #{workspace['project_id']})")

        # Select project
        try:
            project_choice = Display.ask_int("\nEnter project number (0 to cancel):")
            if project_choice == 0:
                return
            if project_choice < 1 or project_choice > len(workspaces):
                Display.print_error("Invalid project number")
                return

            project_id = workspaces[project_choice - 1]['project_id']
        except (ValueError, KeyError):
            Display.print_error("Invalid input")
            return

        # Get project milestones
        workspace = WorkspaceManager.get_workspace(project_id)
        if not workspace:
            Display.print_error("Project not found")
            return

        milestones = workspace['milestones']
        pending_milestones = [m for m in milestones if m['status'] in ['pending', 'revision_requested']]

        if not pending_milestones:
            Display.print_warning("No pending milestones to submit")
            return

        # Display pending milestones
        print("\nPending milestones:")
        for idx, milestone in enumerate(pending_milestones, start=1):
            status_text = f"({milestone['status'].replace('_', ' ').title()})"
            print(f"  [{idx}] {milestone['milestone_name']} {status_text}")
            print(f"      {milestone['description']}")

        # Select milestone
        try:
            milestone_choice = Display.ask_int("\nEnter milestone number (0 to cancel):")
            if milestone_choice == 0:
                return
            if milestone_choice < 1 or milestone_choice > len(pending_milestones):
                Display.print_error("Invalid milestone number")
                return

            selected_milestone = pending_milestones[milestone_choice - 1]
            milestone_id = selected_milestone['milestone_id']
        except (ValueError, KeyError):
            Display.print_error("Invalid input")
            return

        # Get deliverable details
        print(f"\nSubmitting deliverable for: {selected_milestone['milestone_name']}")
        file_path = Display.ask_input("File path (or URL):", allow_empty=True)
        description = Display.ask_input("Description of deliverable:", allow_empty=False)

        # Submit deliverable
        try:
            submission_id = WorkspaceManager.submit_deliverable(
                milestone_id, user_id, file_path if file_path else None, description
            )

            # Update milestone status to submitted
            with DatabaseManager.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE milestones
                    SET status = 'submitted'
                    WHERE milestone_id = %s AND status != 'approved'
                """, (milestone_id,))

            Display.print_success(f"Deliverable submitted successfully! (Submission ID: {submission_id})")
        except Exception as e:
            Display.print_error(f"Failed to submit deliverable: {str(e)}")

    @staticmethod
    def review_deliverable_flow(user_id):
        """Interactive flow for clients to review deliverables"""
        Display.print_header("REVIEW DELIVERABLES")

        # Get client's projects
        workspaces = WorkspaceManager.get_client_workspaces(user_id)

        if not workspaces:
            Display.print_warning("You have no projects")
            return

        # Display projects with pending reviews
        projects_with_submissions = []
        for workspace in workspaces:
            project_data = WorkspaceManager.get_workspace(workspace['project_id'])
            if project_data:
                submitted_milestones = [m for m in project_data['milestones'] if m['status'] == 'submitted']
                if submitted_milestones:
                    projects_with_submissions.append((workspace, submitted_milestones))

        if not projects_with_submissions:
            Display.print_warning("No pending deliverables to review")
            return

        # Display projects
        print("Projects with pending reviews:")
        for idx, (workspace, milestones) in enumerate(projects_with_submissions, start=1):
            print(f"  [{idx}] {workspace['job_title']} - {len(milestones)} pending review(s)")

        # Select project
        try:
            project_choice = Display.ask_int("\nEnter project number (0 to cancel):")
            if project_choice == 0:
                return
            if project_choice < 1 or project_choice > len(projects_with_submissions):
                Display.print_error("Invalid project number")
                return

            selected_workspace, submitted_milestones = projects_with_submissions[project_choice - 1]
        except (ValueError, IndexError):
            Display.print_error("Invalid input")
            return

        # Display submitted milestones
        print(f"\nPending deliverables for: {selected_workspace['job_title']}")
        for idx, milestone in enumerate(submitted_milestones, start=1):
            print(f"  [{idx}] {milestone['milestone_name']}")
            print(f"      {milestone['description']}")

            # Show latest submission
            submissions = WorkspaceManager.get_milestone_submissions(milestone['milestone_id'])
            if submissions:
                latest = submissions[0]
                print(f"      Latest submission (v{latest['version_number']}): {latest['deliverable_description']}")
                if latest['file_path']:
                    print(f"      File: {latest['file_path']}")

        # Select milestone
        try:
            milestone_choice = Display.ask_int("\nEnter milestone number to review (0 to cancel):")
            if milestone_choice == 0:
                return
            if milestone_choice < 1 or milestone_choice > len(submitted_milestones):
                Display.print_error("Invalid milestone number")
                return

            selected_milestone = submitted_milestones[milestone_choice - 1]
            milestone_id = selected_milestone['milestone_id']
        except (ValueError, IndexError):
            Display.print_error("Invalid input")
            return

        # Review options
        print(f"\nReviewing: {selected_milestone['milestone_name']}")
        print("  1. Approve milestone")
        print("  2. Request revision")
        print("  0. Cancel")

        review_choice = Display.ask_input("\nChoose action:")

        if review_choice == "1":
            feedback = Display.ask_input("Feedback (optional):", allow_empty=True)
            try:
                WorkspaceManager.approve_milestone(milestone_id, user_id, feedback if feedback else None)
                Display.print_success(f"Milestone '{selected_milestone['milestone_name']}' approved!")
            except Exception as e:
                Display.print_error(f"Failed to approve milestone: {str(e)}")

        elif review_choice == "2":
            feedback = Display.ask_input("Revision feedback (required):", allow_empty=False)
            try:
                WorkspaceManager.request_revision(milestone_id, user_id, feedback)
                Display.print_success(f"Revision requested for '{selected_milestone['milestone_name']}'")
            except Exception as e:
                Display.print_error(f"Failed to request revision: {str(e)}")
        else:
            Display.print_info("Review cancelled")

    @staticmethod
    def show_workspace_menu(user_type):
        """Show workspace management menu"""
        if user_type == 'freelancer':
            Display.print_menu(
                "Workspace Management",
                [
                    ("1", "View My Active Projects"),
                    ("2", "View Project Details"),
                    ("3", "Submit Deliverable"),
                ]
            )
        else:
            Display.print_menu(
                "Workspace Management",
                [
                    ("1", "View My Client Projects"),
                    ("2", "View Project Details"),
                    ("3", "Review Deliverables"),
                ]
            )
