"""
Freelancer browsing feature for clients to find matching talent.

Allows clients to browse all freelancers or find freelancers matching
specific job requirements based on skills.
"""

from typing import List, Optional

from models.job import Job
from models.user import User, find_freelancers_by_skills, list_users
from utils.display import (
    ask_input,
    divider,
    print_error,
    print_heading,
    print_info,
    print_success,
    print_warning,
)


def _format_freelancer(freelancer: User, index: Optional[int] = None) -> str:
    """Format a freelancer's information for display."""
    prefix = f"[{index}] " if index is not None else ""
    skills = ", ".join(freelancer.skills) if freelancer.skills else "No skills listed"
    location = freelancer.location or "Not specified"

    return (
        f"{prefix}{freelancer.name} (ID: {freelancer.user_id})\n"
        f"   Email: {freelancer.email}\n"
        f"   Location: {location}\n"
        f"   Skills: {skills}\n"
        + ("-" * 50)
    )


def browse_all_freelancers(current_user) -> None:
    """Display all freelancers on the platform."""
    if not current_user or current_user.get("user_type") != "client":
        print_error("Only client accounts can browse freelancers.")
        return

    print_heading("Browse All Freelancers")
    freelancers = list_users("freelancer")

    if not freelancers:
        print_warning("No freelancers registered yet.")
        return

    print_info(f"Found {len(freelancers)} freelancer(s).")
    divider()
    for index, freelancer in enumerate(freelancers, start=1):
        print(_format_freelancer(freelancer, index))


def find_matching_freelancers_for_job(current_user) -> None:
    """Find freelancers matching a specific job's required skills."""
    if not current_user or current_user.get("user_type") != "client":
        print_error("Only client accounts can search for matching freelancers.")
        return

    print_heading("Find Freelancers for Your Job")

    # Get client's jobs
    jobs = Job.get_by_client(current_user["user_id"])
    if not jobs:
        print_warning("You have no posted jobs. Post a job first to find matching freelancers.")
        return

    # Display jobs
    print_info(f"Your posted jobs:")
    divider()
    for index, job in enumerate(jobs, start=1):
        skills = job.required_skills or "No skills specified"
        print(f"[{index}] {job.title} - Status: {job.status}")
        print(f"    Required Skills: {skills}")
    divider()

    # Select a job
    try:
        choice = ask_input("Enter job number to find matching freelancers (or 0 to cancel):")
        if choice == "0":
            return

        job_index = int(choice) - 1
        if job_index < 0 or job_index >= len(jobs):
            print_error("Invalid job number.")
            return

        selected_job = jobs[job_index]
    except ValueError:
        print_error("Please enter a valid number.")
        return

    # Parse required skills
    if not selected_job.required_skills or not selected_job.required_skills.strip():
        print_warning(f"Job '{selected_job.title}' has no required skills specified.")
        print_info("Showing all freelancers instead...")
        required_skills = []
    else:
        required_skills = [
            skill.strip()
            for skill in selected_job.required_skills.split(",")
            if skill.strip()
        ]

    # Find matching freelancers
    print_heading(f"Freelancers Matching: {selected_job.title}")
    if required_skills:
        print_info(f"Looking for skills: {', '.join(required_skills)}")
        freelancers = find_freelancers_by_skills(required_skills)
    else:
        freelancers = list_users("freelancer")

    if not freelancers:
        print_warning("No freelancers found with matching skills.")
        return

    print_success(f"Found {len(freelancers)} matching freelancer(s)!")
    divider()
    for index, freelancer in enumerate(freelancers, start=1):
        print(_format_freelancer(freelancer, index))
        # Show which skills match
        if required_skills:
            matching_skills = [
                skill for skill in freelancer.skills
                if skill in required_skills
            ]
            if matching_skills:
                print(f"   ✓ Matches: {', '.join(matching_skills)}\n")


def freelancer_browser_menu(current_user) -> None:
    """Menu for browsing and finding freelancers."""
    if not current_user or current_user.get("user_type") != "client":
        print_error("Only client accounts can browse freelancers.")
        return

    while True:
        print_heading("Freelancer Browser")
        print(" 1. Browse all freelancers")
        print(" 2. Find freelancers matching my job requirements")
        print(" 0. Back to main menu")
        divider()

        choice = ask_input("Choose an option:")

        if choice == "0":
            break
        elif choice == "1":
            browse_all_freelancers(current_user)
            input("\nPress Enter to continue...")
        elif choice == "2":
            find_matching_freelancers_for_job(current_user)
            input("\nPress Enter to continue...")
        else:
            print_error("Invalid option. Please try again.")
            input("\nPress Enter to continue...")
