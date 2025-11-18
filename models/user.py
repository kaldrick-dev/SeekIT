from database.db_manager import DatabaseManager

class User:
    """User model for freelancer and clients"""

    def __init__(self,user_id=None,name=None,email=None,password_hash=None,location=None,user_type=None,created_at=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash=password_hash
        self.location = location
        self.user_type = user_type
        self.created_at = created_at

    def save(self):
        """Save or update user"""
        with DatabaseManager.get_cursor() as cursor:
            if self.user_id:
                query = """UPDATE users SET name=%s, email=%s, password_hash=%s,location=%s, user_type=%s WHERE user_id=%s"""
                cursor.execute(query,(self.name,self.email,self.password_hash,self.location,self.user_type,self.user_id))
            else:
                query = """INSERT INTO users (name,email,password_hash,location,user_type) VALUES (%s,%s,%s,%s,%s)"""
                cursor.execute(query,(self.name,self.email,self.password_hash,self.location,self.user_type))
                self.user_id = cursor.lastrowid
            return self.user_id

    @classmethod
    def find_by_id(cls,user_id):
        """Find user by ID"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s",(user_id,))
            result = cursor.fetchone()
            return cls(**result) if result else None

    @classmethod
    def find_by_email(cls,email):
        """Find user by email"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s",(email,))
            result = cursor.fetchone()
            return cls(**result) if result else None
    
    def get_skills(self):
        """Get freelancer skills"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""SELECT skill_name, skill_level FROM freelancer_skills WHERE user_id = %s""",(self.user_id,))
            return cursor.fetchall()

    def add_skill(self,skill_name,skill_level):
        """Add skill"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""INSERT INTO freelancer_skills (user_id, skill_name, skill_level) VALUES (%s,%s,%s)""",(self.user_id,skill_name,skill_level))
            return cursor.rowcount > 0


    def delete(self):
        """Delete user from database"""
        if not self.user_id:
            return False
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id = %s", (self.user_id,))
            return cursor.rowcount > 0
        
    def update_skill(self,skill_name,skill_level):
        """Update skill level for existing skill"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""UPDATE freelancer_skills SET skill_level = %s WHERE user_id = %s AND skill_name = %s""",(skill_level,self.user_id,skill_name))
            return cursor.rowcount > 0
    
    def remove_skill(self,skill_name):
        """Remove a skill from freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("DELETE FROM freelancer_skills WHERE user_id = %s AND skill_name = %s",(self.user_id,skill_name))
            return cursor.rowcount > 0
    
    @classmethod
    def get_all(cls,user_type=None):
        """Get all users, optionally filtered by user_type"""
        with DatabaseManager.get_cursor() as cursor:
            if user_type:
                cursor.execute("SELECT * FROM users WHERE user_type = %s ORDER BY created_at DESC",(user_type,))
            else:
                cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            results = cursor.fetchall()
            return [cls(**row) for row in results]
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'user_id':self.user_id,
            'name':self.name,
            'email':self.email,
            'location':self.location,
            'user_type':self.user_type,
            'created_at':self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<User(id={self.user_id}, name='{self.name}, type='{self.user_type}')>"