"""Tiny in-memory application manager used during the prototype phase.

Nothing here talks to the database yet – everything is stored in a Python list
so new contributors can follow along without extra setup.  Swapping to the real
models later will simply require replacing the storage methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from utils.display import (
    ask_input,
    ask_int,
    print_error,
    print_heading,
    print_info,
    print_success,
    print_table,
)


STATUSES = ("pending", "accepted", "rejected")


@dataclass
class ApplicationRecord:
    """Simple container that keeps each application tidy."""

    application_id: int
    job_id: int
    freelancer_id: int
    freelancer_name: str
    cover_letter: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

    def as_row(self) -> tuple[str, str, str, str]:
        """Return a tuple ready for print_table."""
        return (
            str(self.application_id),
            str(self.job_id),
            f"{self.freelancer_name} (#{self.freelancer_id})",
            f"{self.status.title()}",
        )


class ApplicationManager:
    """Lightweight in-memory storage plus a few helper actions."""

    def __init__(self) -> None:
        self._applications: List[ApplicationRecord] = []
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # CRUD-like helpers
    # ------------------------------------------------------------------
    def submit(self, job_id: int, freelancer_id: int, freelancer_name: str, cover_letter: str) -> ApplicationRecord:
        record = ApplicationRecord(
            application_id=self._next_id,
            job_id=job_id,
            freelancer_id=freelancer_id,
            freelancer_name=freelancer_name,
            cover_letter=cover_letter.strip(),
        )
        self._applications.append(record)
        self._next_id += 1
        return record

    def list_for_freelancer(self, freelancer_id: int) -> List[ApplicationRecord]:
        return [app for app in self._applications if app.freelancer_id == freelancer_id]

    def list_for_job(self, job_id: int) -> List[ApplicationRecord]:
        return [app for app in self._applications if app.job_id == job_id]

    def set_status(self, application_id: int, new_status: str) -> Optional[ApplicationRecord]:
        new_status = new_status.lower()
        if new_status not in STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(STATUSES)}")
        application = self._find(application_id)
        if not application:
            return None
        application.status = new_status
        return application

    def _find(self, application_id: int) -> Optional[ApplicationRecord]:
        for app in self._applications:
            if app.application_id == application_id:
                return app
        return None


# A single shared manager instance keeps the CLI state alive while the program runs.
application_manager = ApplicationManager()


# ----------------------------------------------------------------------
# CLI helpers
# ----------------------------------------------------------------------
def _show_table(records: List[ApplicationRecord], empty_message: str) -> None:
    if not records:
        print_info(empty_message)
        return
    rows = [record.as_row() for record in records]
    print_table(("ID", "Job ID", "Freelancer", "Status"), rows)


def _apply_flow(user) -> None:
    job_id = ask_int("Job ID you want to apply to:")
    if job_id is None:
        print_error("Job ID is required.")
        return
    cover_letter = ask_input("Add a short cover letter:")
    if len(cover_letter.strip()) < 5:
        print_error("Try to write at least a few words so the client has context.")
        return
    application = application_manager.submit(job_id, user.user_id, user.name, cover_letter)
    print_success(f"Application #{application.application_id} submitted!")


def _freelancer_menu(user) -> None:
    while True:
        print_heading("Freelancer Applications")
        print(" 1. Apply to a job")
        print(" 2. View my applications")
        print(" 0. Back to main menu")
        choice = ask_input("Choose an option:")
        if choice == "0":
            break
        if choice == "1":
            _apply_flow(user)
        elif choice == "2":
            records = application_manager.list_for_freelancer(user.user_id)
            _show_table(records, "You have not applied to any jobs yet.")
        else:
            print_info("Unknown option, please try again.")


def _client_menu(user) -> None:
    while True:
        print_heading("Client Applications")
        print(" 1. View applications for a job")
        print(" 2. Accept an application")
        print(" 3. Reject an application")
        print(" 0. Back to main menu")
        choice = ask_input("Choose an option:")
        if choice == "0":
            break
        if choice == "1":
            job_id = ask_int("Enter the job ID:")
            if job_id is None:
                print_error("Job ID is required.")
                continue
            records = application_manager.list_for_job(job_id)
            _show_table(records, "No one has applied to this job yet.")
        elif choice in {"2", "3"}:
            application_id = ask_int("Application ID to update:")
            if application_id is None:
                print_error("Application ID is required.")
                continue
            new_status = "accepted" if choice == "2" else "rejected"
            updated = application_manager.set_status(application_id, new_status)
            if not updated:
                print_error("Could not find that application ID.")
            else:
                print_success(f"Application #{application_id} marked as {new_status}.")
        else:
            print_info("Unknown option, please try again.")


def application_manager_menu(current_user) -> None:
    """Entry point called from main.py."""
    if not current_user:
        print_info("Please log in to manage applications.")
        return
    if current_user.user_type == "freelancer":
        _freelancer_menu(current_user)
    elif current_user.user_type == "client":
        _client_menu(current_user)
    else:
        print_info("Only freelancers and clients can use the application manager right now.")
