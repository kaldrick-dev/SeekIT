from unittest import result
from database.db_manager import DatabaseManager

class Job:
    """Job model for client job postings"""

    def __init__(self,job_id=None,client_id=None,title=None,description=None,required_skills=None,budget_min=None,budget_max=None,deadline=None, status='open',created_at=None):
        self.job_id = job_id
        self.client_id = client_id
        self.title = title
        self.description = description
        self.required_skills = required_skills
        self.budget_min = budget_min
        self.budget_max = budget_max
        self.deadline = deadline
        self.status = status # 'open','closed', 'in_progress'
        self.created_at = created_at
    
    def save(self):
        """Save or update job"""
        with DatabaseManager.get_cursor() as cursor:
            if self.job_id:
                query = """UPDATE jobs SET client_id=%s, title=%s, descriptio=%s, required_skills=%s, budget_min=%s, budget_max=%s, daedline=%s, status=%s WHERE job_id=%s"""
                cursor.execute(query,(self.client_id,self.title,self.description,self.required_skills,self.budget_min,self.budget_max,self.deadline,self.status,self.job_id))
            else:
                query = """INSERT INTO jobs (client_id,title,description,required_skills,budget_min,budget_max,deadline,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(query,(self.client_id,self.title,self.description,self.required_skills,self.budget_min,self.budget_max,self.deadline,self.status))
                self.job_id = cursor.lastrowid
            return self.job_id
    
    @classmethod
    def find_by_id(cls,job_id):
        """Find job by ID"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE job_id=%s",(job_id,))
            result = cursor.fetchone()
            return cls(**result) if result else None
    
    @classmethod
    def get_all(cls,status=None):
        """Get all jobs, optionally filtered by status"""
        with DatabaseManager.get_cursor() as cursor:
            if status:
                cursor.execute("SELECT * FROM jobs WHERE status=%s ORDER BY created_at DESC",(status,))
            else:
                cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
            results = cursor.fetchall()
            return [cls(**row) for row in results]
    
    @classmethod
    def get_by_client(cls,client_id):
        """Get all jobs posted by a specific client"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM jobs WHERE client_id = %s ORDER BY created_at DESC",(client_id,))
            results = cursor.fetchall()
            return [cls(**row) for row in results]

    def search(self,keywords=None,min_budget=None,max_budget=None):
        """Search jobs by keywords and budget range"""
        with DatabaseManager.get_cursor() as cursor:
            query = "SELECT * FROM jobs WHERE status = 'open'"
            params = []
            if keywords:
                query += " AND (title LIKE %s OR description LIKE %s OR required_skills LIKE %s)"
                keyword_pattern = f"%{keywords}%"
                params.extend([keyword_pattern,keyword_pattern,keyword_pattern])
            if min_budget:
                query += " AND budget_max >= %s"
                params.append(min_budget)
            if max_budget:
                query += " AND budget_min <= %s"
                params.append(max_budget)
            
            query += " ORDER BY created_at DESC"
            cursor.execute(query,tuple(params))
            results = cursor.fetchall()
            return [Job(**row) for row in results]
    def get_applications(self):
        """Get all applications for this job"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM applications WHERE job_id = %s ORDER BY applied_at DESC",
                         (self.job_id,))
            return cursor.fetchall()

    def delete(self):
        """Delete job"""
        if not self.job_id:
            return False
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("DELETE FROM jobs WHERE job_id = %s", (self.job_id,))
            return cursor.rowcount > 0

    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'job_id': self.job_id,
            'client_id': self.client_id,
            'title': self.title,
            'description': self.description,
            'required_skills': self.required_skills,
            'budget_min': float(self.budget_min) if self.budget_min else None,
            'budget_max': float(self.budget_max) if self.budget_max else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Job(id={self.job_id}, title='{self.title}', status='{self.status}')>"