from database.db_manager import DatabaseManager

class Project:
    """Project model for active freelance projects"""

    def __init__(self, project_id=None, job_id=None, freelancer_id=None, client_id=None,
                 status='active', progress_percentage=0, created_at=None, completed_at=None):
        self.project_id = project_id
        self.job_id = job_id
        self.freelancer_id = freelancer_id
        self.client_id = client_id
        self.status = status  # 'active', 'completed', 'cancelled'
        self.progress_percentage = progress_percentage
        self.created_at = created_at
        self.completed_at = completed_at

    def save(self):
        """Save or update project"""
        with DatabaseManager.get_cursor() as cursor:
            if self.project_id:
                query = """UPDATE projects SET job_id=%s, freelancer_id=%s, client_id=%s,
                           status=%s, progress_percentage=%s, completed_at=%s WHERE project_id=%s"""
                cursor.execute(query, (self.job_id, self.freelancer_id, self.client_id,
                                     self.status, self.progress_percentage, self.completed_at,
                                     self.project_id))
            else:
                query = """INSERT INTO projects (job_id, freelancer_id, client_id, status, progress_percentage)
                           VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (self.job_id, self.freelancer_id, self.client_id,
                                     self.status, self.progress_percentage))
                self.project_id = cursor.lastrowid
            return self.project_id

    @classmethod
    def find_by_id(cls, project_id):
        """Find project by ID"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM projects WHERE project_id = %s", (project_id,))
            result = cursor.fetchone()
            return cls(**result) if result else None

    @classmethod
    def get_by_freelancer(cls, freelancer_id, status=None):
        """Get all projects for a freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            if status:
                cursor.execute("""SELECT * FROM projects WHERE freelancer_id = %s AND status = %s
                               ORDER BY created_at DESC""", (freelancer_id, status))
            else:
                cursor.execute("""SELECT * FROM projects WHERE freelancer_id = %s
                               ORDER BY created_at DESC""", (freelancer_id,))
            results = cursor.fetchall()
            return [cls(**row) for row in results]

    @classmethod
    def get_by_client(cls, client_id, status=None):
        """Get all projects for a client"""
        with DatabaseManager.get_cursor() as cursor:
            if status:
                cursor.execute("""SELECT * FROM projects WHERE client_id = %s AND status = %s
                               ORDER BY created_at DESC""", (client_id, status))
            else:
                cursor.execute("""SELECT * FROM projects WHERE client_id = %s
                               ORDER BY created_at DESC""", (client_id,))
            results = cursor.fetchall()
            return [cls(**row) for row in results]

    def get_milestones(self):
        """Get all milestones for this project"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""SELECT * FROM milestones WHERE project_id = %s
                           ORDER BY order_number ASC""", (self.project_id,))
            return cursor.fetchall()

    def add_milestone(self, milestone_name, description, due_date, order_number):
        """Add milestone to project"""
        with DatabaseManager.get_cursor() as cursor:
            query = """INSERT INTO milestones (project_id, milestone_name, description, due_date, order_number)
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (self.project_id, milestone_name, description, due_date, order_number))
            return cursor.lastrowid

    def update_progress(self, progress_percentage):
        """Update project progress"""
        self.progress_percentage = progress_percentage
        if progress_percentage >= 100:
            self.status = 'completed'
        return self.save()

    def complete(self):
        """Mark project as completed"""
        from datetime import datetime
        self.status = 'completed'
        self.progress_percentage = 100
        self.completed_at = datetime.now()
        return self.save()

    def cancel(self):
        """Cancel project"""
        self.status = 'cancelled'
        return self.save()

    def delete(self):
        """Delete project"""
        if not self.project_id:
            return False
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("DELETE FROM projects WHERE project_id = %s", (self.project_id,))
            return cursor.rowcount > 0

    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'project_id': self.project_id,
            'job_id': self.job_id,
            'freelancer_id': self.freelancer_id,
            'client_id': self.client_id,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f"<Project(id={self.project_id}, status='{self.status}', progress={self.progress_percentage}%)>"