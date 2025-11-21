"""
Simple CLI helpers that let a client post and review jobs.

The functions here expect a `current_user` dictionary that contains
`user_id`, `name`, and `user_type`.  This keeps the code easy to test
and easy to plug into the larger CLI loop later on.
"""

from datetime import datetime
from typing import Dict, Optional, Union

from models.job import Job
from utils.display import (
    ask_input,
    print_error,
    print_heading,
    print_info,
    print_menu,
    print_success,
    print_warning,
)


def _prompt_number(label: str) -> Optional[float]:
    """
    Ask the user for a number but allow them to skip by pressing Enter.
    """
    while True:
        raw_value = ask_input(f"{label} (press Enter to skip):", allow_empty=True)
        if raw_value == "":
            return None
        try:
            return float(raw_value)
        except ValueError:
            print_error("Please enter a number like 500 or 1200.50.")


def _prompt_deadline() -> Optional[str]:
    """Collect a YYYY-MM-DD string or let the user leave it blank."""
    while True:
        raw_value = ask_input("Deadline (YYYY-MM-DD, optional):", allow_empty=True)
        if raw_value == "":
            return None
        try:
            datetime.strptime(raw_value, "%Y-%m-%d")
            return raw_value
        except ValueError:
            print_error("Invalid date format. Please try again.")


def _collect_job_details() -> Dict[str, Optional[Union[str, float]]]:
    """Grab all the information we need to create a job."""
    title = ask_input("Job title:", allow_empty=False)
    description = ask_input("Describe the work:", allow_empty=False)
    skill_list = ask_input("Required skills (comma separated):", allow_empty=True)
    budget_min = _prompt_number("Minimum budget")
    budget_max = _prompt_number("Maximum budget")
    deadline = _prompt_deadline()

    # Clean up the skills so spacing looks tidy when we print the job later.
    clean_skills = ", ".join(
        part.strip() for part in skill_list.split(",") if part.strip()
    )

    return {
        "title": title,
        "description": description,
        "required_skills": clean_skills,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "deadline": deadline,
    }


def _format_job(job: Job, index: Optional[int] = None) -> str:
    """Return a friendly block of text that describes a job posting."""
    prefix = f"[{index}] " if index is not None else ""
    skills = job.required_skills or "Not specified"
    line_one = f"{prefix}{job.title} • Status: {job.status}"
    line_two = f"   Skills: {skills}"
    budget = "Budget: not provided"
    if job.budget_min is not None or job.budget_max is not None:
        budget = (
            f"Budget: ${job.budget_min or 0:.0f} - "
            f"${job.budget_max or job.budget_min or 0:.0f}"
        )
    details = [
        line_one,
        line_two,
        f"   {budget}",
        f"   Deadline: {job.deadline or 'Flexible'}",
        "-" * 50,
    ]
    return "\n".join(details)


def post_new_job(current_user):
    """
    Collect job information and save it to the database.

    Returns the Job instance or None when posting is not allowed.
    """

    if not current_user or current_user.get("user_type") != "client":
        print_error("Only client accounts can post jobs.")
        return None

    print_heading("Post a New Job")
    print_info("We only ask for a few details so freelancers know what you need.")
    job_details = _collect_job_details()

    job = Job(client_id=current_user["user_id"], **job_details)
    job_id = job.save()

    print_success(f"Job posted with ID #{job_id}")
    print(_format_job(job))
    return job


def show_client_jobs(current_user):
    """Display all jobs that belong to the current client."""

    if not current_user or current_user.get("user_type") != "client":
        print_error("Only client accounts can view posted jobs.")
        return []

    print_heading("My Posted Jobs")
    jobs = Job.get_by_client(current_user["user_id"])
    if not jobs:
        print_warning("You have not posted any jobs yet.")
        return []

    print_info(f"You have {len(jobs)} job(s).")
    for index, job in enumerate(jobs, start=1):
        print(_format_job(job, index))
    return jobs


def job_posting_menu(current_user):
    """
    Very small menu loop so the rest of the app can call a single function.
    """

    if not current_user or current_user.get("user_type") != "client":
        print_error("Please sign in with a client account to use job tools.")
        return

    menu_choices = [
        ("1", "Post a new job"),
        ("2", "View my jobs"),
    ]

    while True:
        print_menu("Job Posting Menu", menu_choices)
        choice = ask_input("Choose an option:")

        if choice == "1":
            post_new_job(current_user)
        elif choice == "2":
            show_client_jobs(current_user)
        elif choice == "0":
            print_info("Returning to the main menu...")
            break
        else:
            print_error("Please choose 1, 2, or 0.")

