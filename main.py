"""Entry point for the SeekIT prototype CLI."""

from typing import Optional

from features.auth import list_users_flow, login_user_flow, register_user_flow
from features.job_posting import job_posting_menu
from models.user import User
from utils.display import (
    ask_input,
    divider,
    print_heading,
    print_info,
    print_success,
)


def main() -> None:
    """Run a basic interactive loop."""
    print_heading("SeekIT Prototype")
    current_user: Optional[User] = None

    while True:
        if current_user:
            print_success(
                f"Logged in as {current_user.name} ({current_user.user_type.title()})"
            )
        else:
            print_info("You are not logged in.")

        divider()
        print(" 1. Register new account")
        print(" 2. Log in to existing account")
        print(" 3. List registered users")
        print(" 4. Log out")
        if current_user and current_user.user_type == "client":
            print(" 5. Job posting tools")
        print(" 0. Exit")
        divider()

        choice = ask_input("Choose an option:")
        if choice == "0":
            print_info("Goodbye!")
            break

        if choice == "1":
            user = register_user_flow()
            if user:
                current_user = user
        elif choice == "2":
            if current_user:
                print_info("You are already logged in. Log out first to switch users.")
            else:
                user = login_user_flow()
                if user:
                    current_user = user
        elif choice == "3":
            list_users_flow()
        elif choice == "4":
            if current_user:
                print_info(f"Logged out {current_user.name}.")
                current_user = None
            else:
                print_info("No user is logged in.")
        elif choice == "5":
            if not current_user:
                print_info("Log in as a client to use job tools.")
            elif current_user.user_type != "client":
                print_info("Only client accounts can post or review jobs.")
            else:
                job_posting_menu(
                    {
                        "user_id": current_user.user_id,
                        "name": current_user.name,
                        "user_type": current_user.user_type,
                    }
                )
        else:
            print_info("Unknown option. Please try again.")

        divider()


if __name__ == "__main__":
    main()
