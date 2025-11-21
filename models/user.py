"""MySQL-backed user model for the authentication feature."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from database.db_manager import DatabaseManager
from utils.security import verify_password


@dataclass
class User:
    """Represents a platform user."""

    user_id: int
    name: str
    email: str
    password_hash: str = field(repr=False)
    location: str = ""
    user_type: str = "freelancer"
    created_at: str = ""
    skills: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return safe data for printing or JSON."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "location": self.location,
            "user_type": self.user_type,
            "created_at": self.created_at,
            "skills": list(self.skills),
        }


def register_user(
    name: str,
    email: str,
    password_hash: str,
    location: str,
    user_type: str,
    skills: Optional[List[str]] = None,
) -> User:
    """Insert a new user row and return the created User."""
    normalized_email = email.strip().lower()

    with DatabaseManager.get_cursor() as cursor:
        # Check if user already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE LOWER(email) = %s",
            (normalized_email,)
        )
        if cursor.fetchone():
            raise ValueError("A user with that email already exists.")

        # Insert new user
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, location, user_type)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name.strip(), normalized_email, password_hash, location.strip(), user_type)
        )
        user_id = cursor.lastrowid

        # Add skills if freelancer
        if user_type == "freelancer" and skills:
            _replace_skills(cursor, user_id, skills)

        # Fetch the created user
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        return _build_user(cursor, row)


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Validate login credentials."""
    user = get_user_by_email(email)
    if not user:
        return None
    if verify_password(password, user.password_hash):
        return user
    return None


def get_user_by_email(email: str) -> Optional[User]:
    """Return a user by email if it exists."""
    normalized = email.strip().lower()

    with DatabaseManager.get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(email) = %s LIMIT 1",
            (normalized,)
        )
        row = cursor.fetchone()
        return _build_user(cursor, row) if row else None


def list_users(user_type: Optional[str] = None) -> List[User]:
    """Return all registered users, optionally filtered by role."""
    with DatabaseManager.get_cursor() as cursor:
        if user_type:
            cursor.execute(
                "SELECT * FROM users WHERE user_type = %s ORDER BY created_at DESC",
                (user_type.lower(),)
            )
        else:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")

        rows = cursor.fetchall()
        return [_build_user(cursor, row) for row in rows]


def find_freelancers_by_skills(required_skills: List[str]) -> List[User]:
    """Find freelancers that match any of the required skills."""
    if not required_skills:
        return list_users("freelancer")

    with DatabaseManager.get_cursor() as cursor:
        # Build a query to find freelancers with matching skills
        placeholders = ", ".join(["%s"] * len(required_skills))
        query = f"""
            SELECT DISTINCT u.*
            FROM users u
            INNER JOIN freelancer_skills fs ON u.user_id = fs.user_id
            WHERE u.user_type = 'freelancer'
            AND fs.skill_name IN ({placeholders})
            ORDER BY u.created_at DESC
        """
        cursor.execute(query, tuple(required_skills))
        rows = cursor.fetchall()
        return [_build_user(cursor, row) for row in rows]


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _build_user(cursor, row) -> User:
    """Convert a database row plus related skills to a User dataclass."""
    if row is None:
        raise ValueError("Cannot build a user from an empty row.")

    skills = _fetch_skills(cursor, row["user_id"])

    return User(
        user_id=row["user_id"],
        name=row["name"],
        email=row["email"],
        password_hash=row["password_hash"],
        location=row["location"] or "",
        user_type=row["user_type"],
        created_at=str(row["created_at"]) if row["created_at"] else "",
        skills=skills,
    )


def _fetch_skills(cursor, user_id: int) -> List[str]:
    """Fetch skills for a user."""
    cursor.execute(
        "SELECT skill_name FROM freelancer_skills WHERE user_id = %s ORDER BY skill_name ASC",
        (user_id,)
    )
    return [record["skill_name"] for record in cursor.fetchall()]


def _replace_skills(cursor, user_id: int, skills: List[str]) -> None:
    """Replace all skills for a user."""
    cursor.execute("DELETE FROM freelancer_skills WHERE user_id = %s", (user_id,))

    for skill in skills:
        if skill.strip():
            cursor.execute(
                "INSERT INTO freelancer_skills (user_id, skill_name) VALUES (%s, %s)",
                (user_id, skill.strip())
            )
