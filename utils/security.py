"""Password hashing helpers using bcrypt."""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password with bcrypt and return a UTF-8 string."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    """Compare a plain password against the stored bcrypt hash."""
    if not stored_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
