import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import DatabaseConfig


class DatabaseManager:
    """Lightweight wrapper around a single SQLite database file."""

    _connection = None
    _db_path = Path(DatabaseConfig.SQLITE_DB_PATH)

    @classmethod
    def _ensure_connection(cls) -> sqlite3.Connection:
        if cls._connection is None:
            cls._db_path.parent.mkdir(parents=True, exist_ok=True)
            cls._connection = sqlite3.connect(cls._db_path)
            cls._connection.row_factory = sqlite3.Row
            cls._ensure_tables()
        return cls._connection

    @classmethod
    def _ensure_tables(cls) -> None:
        cursor = cls._connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                required_skills TEXT,
                budget_min REAL,
                budget_max REAL,
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.close()
        cls._connection.commit()

    @classmethod
    @contextmanager
    def get_cursor(cls):
        """Context manager that yields a cursor and commits on success."""
        connection = cls._ensure_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except sqlite3.Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
