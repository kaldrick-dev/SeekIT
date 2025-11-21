"""Entry point for the SeekIT prototype CLI."""

from typing import Optional

from features.application_manager import application_manager_menu
from features.auth import list_users_flow, login_user_flow, register_user_flow
from features.freelancer_browser import freelancer_browser_menu
from features.job_posting import job_posting_menu
from features.job_search import job_search_menu
from features.profile import ProfileManager
from features.portfolio import PortfolioManager
from features.workspace import WorkspaceManager
from models.user import User
from utils.display import (
    Display,
    ask_input,
    divider,
    print_heading,
    print_info,
    print_success,
)


def profile_menu(user: User) -> None:
    """Display profile management menu."""
    while True:
        Display.clear_screen()
        ProfileManager.show_profile_menu(user)

        choice = ask_input("Choose an option:")

        if choice == "0":
            break
        elif choice == "1":
            Display.clear_screen()
            ProfileManager.display_profile(user)
            Display.pause()
        elif choice == "2":
            Display.clear_screen()
            if user.skills:
                ProfileManager.display_skills(user.skills)
            else:
                Display.print_warning("No skills to display")
            Display.pause()
        elif choice == "3":
            Display.print_info("Profile update feature coming soon!")
            Display.pause()
        elif choice == "4":
            Display.print_info("Skill management feature coming soon!")
            Display.pause()
        else:
            Display.print_warning("Invalid option. Please try again.")
            Display.pause()


def portfolio_menu(user: User) -> None:
    """Display portfolio management menu."""
    while True:
        Display.clear_screen()
        PortfolioManager.show_portfolio_menu()

        choice = ask_input("Choose an option:")

        if choice == "0":
            break
        elif choice == "1":
            Display.clear_screen()
            PortfolioManager.display_portfolio(user.user_id)
            Display.pause()
        elif choice == "2":
            Display.clear_screen()
            from models.portfolio import Portfolio
            stats = Portfolio.get_stats(user.user_id)
            PortfolioManager.display_stats(stats)
            Display.pause()
        elif choice == "3":
            Display.clear_screen()
            from models.portfolio import Portfolio
            projects = Portfolio.get_by_freelancer(user.user_id)
            PortfolioManager.display_projects(projects)
            Display.pause()
        elif choice == "4":
            Display.clear_screen()
            from models.portfolio import Portfolio
            reviews = Portfolio.get_reviews(user.user_id)
            PortfolioManager.display_reviews(reviews)
            Display.pause()
        elif choice == "5":
            Display.print_info("Portfolio export feature coming soon!")
            Display.pause()
        else:
            Display.print_warning("Invalid option. Please try again.")
            Display.pause()


def workspace_menu(user: User) -> None:
    """Display workspace management menu."""
    while True:
        Display.clear_screen()
        WorkspaceManager.show_workspace_menu(user.user_type)

        choice = ask_input("Choose an option:")

        if choice == "0":
            break
        elif choice == "1":
            Display.clear_screen()
            WorkspaceManager.display_workspaces(user.user_id, user.user_type)
            Display.pause()
        elif choice == "2":
            Display.clear_screen()
            project_id = Display.ask_int("Enter Project ID:")
            WorkspaceManager.display_workspace_details(project_id)
            Display.pause()
        elif choice == "3":
            Display.clear_screen()
            if user.user_type == "freelancer":
                WorkspaceManager.submit_deliverable_flow(user.user_id)
            else:
                WorkspaceManager.review_deliverable_flow(user.user_id)
            Display.pause()
        else:
            Display.print_warning("Invalid option. Please try again.")
            Display.pause()


def main() -> None:
    """Run a basic interactive loop."""
    Display.print_welcome_banner()
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
        print(" 5. Search open jobs")
        if current_user:
            print(" 6. Application manager")
            print(" 8. View Profile")
            print(" 10. Workspace Manager")
        if current_user and current_user.user_type == "client":
            print(" 7. Job posting tools")
            print(" 11. Browse freelancers")
        if current_user and current_user.user_type == "freelancer":
            print(" 9. View Portfolio")
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
            if not current_user:
                print_info("Log in to view registered users.")
            else:
                list_users_flow()
        elif choice == "4":
            if current_user:
                print_info(f"Logged out {current_user.name}.")
                current_user = None
            else:
                print_info("No user is logged in.")
        elif choice == "5":
            job_search_menu()
        elif choice == "6":
            if not current_user:
                print_info("Log in to manage applications.")
            else:
                application_manager_menu(current_user)
        elif choice == "7":
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
        elif choice == "8":
            if not current_user:
                print_info("Log in to view your profile.")
            else:
                profile_menu(current_user)
        elif choice == "9":
            if not current_user:
                print_info("Log in as a freelancer to view portfolio.")
            elif current_user.user_type != "freelancer":
                print_info("Only freelancer accounts have portfolios.")
            else:
                portfolio_menu(current_user)
        elif choice == "10":
            if not current_user:
                print_info("Log in to access workspace manager.")
            else:
                workspace_menu(current_user)
        elif choice == "11":
            if not current_user:
                print_info("Log in as a client to browse freelancers.")
            elif current_user.user_type != "client":
                print_info("Only client accounts can browse freelancers.")
            else:
                freelancer_browser_menu(
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
