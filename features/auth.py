"""Auth-related helper flows for the CLI prototype."""

from typing import List, Optional

from models.user import User, authenticate_user, list_users, register_user
from utils.display import (
    ask_input,
    divider,
    print_error,
    print_heading,
    print_info,
    print_success,
    print_warning,
)
from utils.security import hash_password
from utils.validation import (
    parse_skill_list,
    validate_email,
    validate_non_empty,
    validate_password_strength,
    validate_user_type,
)


def _collect_credentials() -> Optional[dict]:
    """Ask the user for details and validate them."""
    name = ask_input("Name:")
    email = ask_input("Email address:")
    location = ask_input("Location (optional):", allow_empty=True)
    user_type = ask_input("Are you a freelancer or client?:")
    password = ask_input("Password:")

    try:
        validate_non_empty(name, "Name")
        validate_email(email)
        normalized_user_type = validate_user_type(user_type)
        validate_password_strength(password)
    except ValueError as exc:
        print_error(str(exc))
        return None

    skills: List[str] = []
    if normalized_user_type == "freelancer":
        skills_raw = ask_input("Skills (comma separated):")
        try:
            skills = parse_skill_list(skills_raw)
        except ValueError as exc:
            print_error(str(exc))
            return None

    return {
        "name": name.strip(),
        "email": email.strip(),
        "location": location.strip(),
        "user_type": normalized_user_type,
        "password": password,
        "skills": skills,
    }


def register_user_flow() -> Optional[User]:
    """Create a new user and return it."""
    print_heading("Create Account")
    data = _collect_credentials()
    if not data:
        return None

    try:
        user = register_user(
            name=data["name"],
            email=data["email"],
            password_hash=hash_password(data["password"]),
            location=data["location"],
            user_type=data["user_type"],
            skills=data["skills"],
        )
    except ValueError as exc:
        print_warning(str(exc))
        return None

    print_success(f"Welcome aboard, {user.name}! Your account is ready.")
    if user.user_type == "freelancer" and user.skills:
        print_info(f"Saved skills: {', '.join(user.skills)}")
    return user


def login_user_flow() -> Optional[User]:
    """Very small login routine."""
    print_heading("Log In")
    email = ask_input("Email address:")
    password = ask_input("Password:")

    try:
        validate_email(email)
        validate_password_strength(password)
    except ValueError as exc:
        print_error(str(exc))
        return None

    user = authenticate_user(email, password)
    if not user:
        print_error("Invalid email or password. Please try again.")
        return None

    print_success(f"Welcome back, {user.name} ({user.user_type.title()})!")
    return user


def list_users_flow() -> None:
    """Print a small table with the stored users."""
    print_heading("Users")
    filter_type = ask_input("Filter by type (Enter to show all):", allow_empty=True)
    users = list_users(filter_type.strip().lower() or None)

    if not users:
        print_info("No users stored yet. Create one from the menu.")
        return

    divider()
    for user in users:
        skills = ", ".join(user.skills) if user.skills else "N/A"
        print(
            f"#{user.user_id} {user.name} <{user.email}> "
            f"- {user.user_type.title()} @ {user.location or 'N/A'} | Skills: {skills}"
        )
    divider()





