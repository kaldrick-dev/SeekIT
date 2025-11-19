import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_BASE_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_SQLITE_PATH = os.getenv("SQLITE_DB_PATH", str(_BASE_DIR / "seekit.sqlite3"))


class DatabaseConfig:
    """Environment-driven database configuration.

    We keep the MySQL settings for forward-compatibility while the
    prototype uses SQLite for the authentication feature.
    """

    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", 3306))
    USER = os.getenv("DB_USER", "root")
    PASSWORD = os.getenv("DB_PASS", "")
    DATABASE = os.getenv("DB_NAME", "SeekIT")

    SQLITE_DB_PATH = _DEFAULT_SQLITE_PATH
