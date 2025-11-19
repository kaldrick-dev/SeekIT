"""Tiny validation helpers with friendly error messages."""

import re
from typing import List

EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
ALLOWED_USER_TYPES = {"freelancer", "client"}


def validate_non_empty(value: str, field_name: str) -> None:
    """Make sure a field is not blank."""
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty.")


def validate_email(email: str) -> None:
    """Basic email validation for the prototype."""
    validate_non_empty(email, "Email")
    if not EMAIL_RE.match(email):
        raise ValueError("Please enter a valid email address.")


def validate_password_strength(password: str) -> None:
    """Keep password rules simple but safe enough."""
    validate_non_empty(password, "Password")
    if len(password) < 6:
        raise ValueError("Password should be at least 6 characters long.")


def validate_user_type(user_type: str) -> str:
    """Ensure the selected user type exists."""
    validate_non_empty(user_type, "User type")
    normalized = user_type.lower()
    if normalized not in ALLOWED_USER_TYPES:
        allowed = ", ".join(sorted(ALLOWED_USER_TYPES))
        raise ValueError(f"User type must be one of: {allowed}.")
    return normalized


def parse_skill_list(raw_input: str) -> List[str]:
    """Split a comma-separated string into a clean list of skills."""
    skills = [skill.strip() for skill in raw_input.split(",") if skill.strip()]
    if not skills:
        raise ValueError("Please provide at least one skill.")
    return skills
