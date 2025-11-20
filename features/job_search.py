"""
Tiny helpers that let anyone browse open jobs from the CLI.

The goal is to keep the flow friendly for newcomers, so each function only does
one thing and includes short comments that explain what is happening.
"""

from typing import Dict, List, Optional, Union

from models.job import Job
from utils.display import (
    ask_input,
    print_error,
    print_heading,
    print_info,
    print_menu,
    print_table,
    print_warning,
)


def _prompt_budget(label: str) -> Optional[float]:
    """Collect a budget filter. Empty input means 'skip this filter'."""
    while True:
        raw_value = ask_input(f"{label} (press Enter to skip):", allow_empty=True)
        if raw_value == "":
            return None
        try:
            return float(raw_value)
        except ValueError:
            print_error("Please enter numbers only, e.g. 1200 or 500.50.")


def _collect_filters() -> Dict[str, Optional[Union[str, float]]]:
    """Ask the user which filters to apply."""
    keywords = ask_input("Keywords (title, skills, etc.):", allow_empty=True)
    min_budget = _prompt_budget("Minimum budget")
    max_budget = _prompt_budget("Maximum budget")

    return {
        "keywords": keywords or None,
        "min_budget": min_budget,
        "max_budget": max_budget,
    }


def _jobs_to_rows(jobs: List[Job]) -> List[List[str]]:
    """Convert Job objects into table-friendly rows."""
    rows: List[List[str]] = []
    for job in jobs:
        if job.budget_min is None and job.budget_max is None:
            budget_text = "Not provided"
        elif job.budget_min is None:
            budget_text = f"Up to ${job.budget_max:.0f}"
        elif job.budget_max is None:
            budget_text = f"From ${job.budget_min:.0f}"
        else:
            budget_text = f"${job.budget_min:.0f} - ${job.budget_max:.0f}"
        rows.append(
            [
                str(job.job_id or "-"),
                job.title or "Untitled",
                budget_text,
                job.required_skills or "Skills not listed",
            ]
        )
    return rows


def search_open_jobs() -> List[Job]:
    """
    Run a one-off search and print the results.

    Returns the list so tests can inspect it later.
    """
    print_heading("Search Open Jobs")
    print_info("Leave any field blank to skip that filter.")

    filters = _collect_filters()
    job_gateway = Job()
    results = job_gateway.search(
        keywords=filters["keywords"],
        min_budget=filters["min_budget"],
        max_budget=filters["max_budget"],
    )

    if not results:
        print_warning("No open jobs matched those filters.")
        return []

    print_info(f"Showing {len(results)} open job(s).")
    print_table(
        headers=("ID", "Title", "Budget", "Skills"),
        rows=_jobs_to_rows(results),
    )
    return results


def job_search_menu() -> None:
    """Mini loop so the feature plugs nicely into the global CLI."""
    menu_choices = [
        ("1", "Search open jobs"),
        ("0", "Back to previous menu"),
    ]

    while True:
        choice = print_menu("Job Search", menu_choices)
        if choice == "1":
            search_open_jobs()
        elif choice == "0":
            print_info("Returning to the main menu...")
            break
        else:
            print_error("Please choose 1 or 0.")

