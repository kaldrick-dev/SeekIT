"""SQLite-backed user model for the authentication feature."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator, List, Optional

from config.settings import DatabaseConfig
from utils.security import verify_password

_DB_PATH = Path(DatabaseConfig.SQLITE_DB_PATH)


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
    _ensure_database_setup()
    with _get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, location, user_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name.strip(), normalized_email, password_hash, location.strip(), user_type),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("A user with that email already exists.") from exc

        user_id = cursor.lastrowid
        if user_type == "freelancer" and skills:
            _replace_skills(cursor, user_id, skills)

        row = _fetch_user_row(cursor, user_id)
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
    _ensure_database_setup()
    normalized = email.strip().lower()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE LOWER(email) = ? LIMIT 1",
            (normalized,),
        )
        row = cursor.fetchone()
        return _build_user(cursor, row) if row else None


def list_users(user_type: Optional[str] = None) -> List[User]:
    """Return all registered users, optionally filtered by role."""
    _ensure_database_setup()
    with _get_connection() as conn:
        cursor = conn.cursor()
        if user_type:
            cursor.execute(
                "SELECT * FROM users WHERE user_type = ? ORDER BY created_at DESC",
                (user_type.lower(),),
            )
        else:
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [_build_user(cursor, row) for row in rows]


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #


def _ensure_database_setup() -> None:
    """Make sure the SQLite file and tables exist."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                location TEXT,
                user_type TEXT NOT NULL CHECK(user_type IN ('freelancer', 'client')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS freelancer_skills (
                skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
            """
        )


@contextmanager
def _get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager that handles commits and rollbacks."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def _build_user(cursor: sqlite3.Cursor, row: sqlite3.Row) -> User:
    """Convert a sqlite row plus related skills to a User dataclass."""
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
        created_at=row["created_at"] or "",
        skills=skills,
    )


def _fetch_user_row(cursor: sqlite3.Cursor, user_id: int) -> sqlite3.Row:
    cursor.execute("SELECT * FROM users WHERE user_id = ? LIMIT 1", (user_id,))
    row = cursor.fetchone()
    if not row:
        raise LookupError("User could not be found after creation.")
    return row


def _fetch_skills(cursor: sqlite3.Cursor, user_id: int) -> List[str]:
    cursor.execute(
        "SELECT skill_name FROM freelancer_skills WHERE user_id = ? ORDER BY skill_name ASC",
        (user_id,),
    )
    return [record["skill_name"] for record in cursor.fetchall()]


def _replace_skills(cursor: sqlite3.Cursor, user_id: int, skills: List[str]) -> None:
    cursor.execute("DELETE FROM freelancer_skills WHERE user_id = ?", (user_id,))
    cursor.executemany(
        "INSERT INTO freelancer_skills (user_id, skill_name) VALUES (?, ?)",
        [(user_id, skill.strip()) for skill in skills if skill.strip()],
    )