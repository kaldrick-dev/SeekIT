from database.db_manager import DatabaseManager

class Application:
    """Application model for freelancer job applications"""

    def __init__(self, application_id=None, job_id=None, freelancer_id=None,
                 cover_letter=None, status='pending', applied_at=None):
        self.application_id = application_id
        self.job_id = job_id
        self.freelancer_id = freelancer_id
        self.cover_letter = cover_letter
        self.status = status  # 'pending', 'accepted', 'rejected'
        self.applied_at = applied_at

    def save(self):
        """Save or update application"""
        with DatabaseManager.get_cursor() as cursor:
            if self.application_id:
                query = """UPDATE applications SET job_id=%s, freelancer_id=%s,
                           cover_letter=%s, status=%s WHERE application_id=%s"""
                cursor.execute(query, (self.job_id, self.freelancer_id,
                                     self.cover_letter, self.status, self.application_id))
            else:
                query = """INSERT INTO applications (job_id, freelancer_id, cover_letter, status)
                           VALUES (%s, %s, %s, %s)"""
                cursor.execute(query, (self.job_id, self.freelancer_id,
                                     self.cover_letter, self.status))
                self.application_id = cursor.lastrowid
            return self.application_id

    @classmethod
    def find_by_id(cls, application_id):
        """Find application by ID"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM applications WHERE application_id = %s", 
                         (application_id,))
            result = cursor.fetchone()
            return cls(**result) if result else None

    @classmethod
    def get_by_job(cls, job_id, status=None):
        """Get all applications for a specific job"""
        with DatabaseManager.get_cursor() as cursor:
            if status:
                cursor.execute("""SELECT * FROM applications WHERE job_id = %s AND status = %s
                               ORDER BY applied_at DESC""", (job_id, status))
            else:
                cursor.execute("""SELECT * FROM applications WHERE job_id = %s
                               ORDER BY applied_at DESC""", (job_id,))
            results = cursor.fetchall()
            return [cls(**row) for row in results]

    @classmethod
    def get_by_freelancer(cls, freelancer_id, status=None):
        """Get all applications by a specific freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            if status:
                cursor.execute("""SELECT * FROM applications WHERE freelancer_id = %s AND status = %s
                               ORDER BY applied_at DESC""", (freelancer_id, status))
            else:
                cursor.execute("""SELECT * FROM applications WHERE freelancer_id = %s
                               ORDER BY applied_at DESC""", (freelancer_id,))
            results = cursor.fetchall()
            return [cls(**row) for row in results]

    @classmethod
    def check_existing(cls, job_id, freelancer_id):
        """Check if freelancer already applied to this job"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""SELECT * FROM applications WHERE job_id = %s 
                           AND freelancer_id = %s""", (job_id, freelancer_id))
            result = cursor.fetchone()
            return cls(**result) if result else None

    def accept(self):
        """Accept application and auto-create workspace"""
        from features.workspace import WorkspaceManager

        self.status = 'accepted'
        self.save()

        # Get job details to extract client_id
        job = self.get_job_details()
        if job:
            # Auto-create workspace
            project_id = WorkspaceManager.create_workspace(
                application_id=self.application_id,
                job_id=self.job_id,
                freelancer_id=self.freelancer_id,
                client_id=job['client_id']
            )
            return project_id

        return self.application_id

    def get_job_details(self):
        """Get job details for this application"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (self.job_id,))
            return cursor.fetchone()

    def reject(self):
        """Reject application"""
        self.status = 'rejected'
        return self.save()

    def delete(self):
        """Delete application"""
        if not self.application_id:
            return False
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("DELETE FROM applications WHERE application_id = %s", 
                         (self.application_id,))
            return cursor.rowcount > 0

    def to_dict(self):
        """Convert application to dictionary"""
        return {
            'application_id': self.application_id,
            'job_id': self.job_id,
            'freelancer_id': self.freelancer_id,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }

    def __repr__(self):
        return f"<Application(id={self.application_id}, job_id={self.job_id}, status='{self.status}')>"