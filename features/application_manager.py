"""Tiny in-memory application manager used during the prototype phase.

Nothing here talks to the database yet – everything is stored in a Python list
so new contributors can follow along without extra setup.  Swapping to the real
models later will simply require replacing the storage methods.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from features.job_search import search_open_jobs
from utils.display import (
    ask_input,
    ask_int,
    print_error,
    print_heading,
    print_info,
    print_success,
    print_table,
    print_warning,
)
from features.workspace import WorkspaceManager
from models.job import Job
from database.db_manager import DatabaseManager


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
    """Database-backed application manager using MySQL."""

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # CRUD-like helpers
    # ------------------------------------------------------------------
    def submit(self, job_id: int, freelancer_id: int, freelancer_name: str, cover_letter: str) -> ApplicationRecord:
        """Submit a new application to the database"""
        with DatabaseManager.get_cursor() as cursor:
            query = """
                INSERT INTO applications (job_id, freelancer_id, cover_letter, status)
                VALUES (%s, %s, %s, 'pending')
            """
            cursor.execute(query, (job_id, freelancer_id, cover_letter.strip()))
            application_id = cursor.lastrowid

            # Fetch the created application
            cursor.execute("""
                SELECT a.*, u.name as freelancer_name
                FROM applications a
                JOIN users u ON a.freelancer_id = u.user_id
                WHERE a.application_id = %s
            """, (application_id,))
            row = cursor.fetchone()

            return self._row_to_record(row)

    def list_for_freelancer(self, freelancer_id: int) -> List[ApplicationRecord]:
        """Get all applications for a freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as freelancer_name
                FROM applications a
                JOIN users u ON a.freelancer_id = u.user_id
                WHERE a.freelancer_id = %s
                ORDER BY a.applied_at DESC
            """, (freelancer_id,))
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def list_for_job(self, job_id: int) -> List[ApplicationRecord]:
        """Get all applications for a job"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as freelancer_name
                FROM applications a
                JOIN users u ON a.freelancer_id = u.user_id
                WHERE a.job_id = %s
                ORDER BY a.applied_at DESC
            """, (job_id,))
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def list_for_client(self, client_id: int) -> List[ApplicationRecord]:
        """Get all applications for all jobs posted by a client"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as freelancer_name
                FROM applications a
                JOIN users u ON a.freelancer_id = u.user_id
                JOIN jobs j ON a.job_id = j.job_id
                WHERE j.client_id = %s
                ORDER BY a.applied_at DESC
            """, (client_id,))
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def get_application(self, application_id: int) -> Optional[ApplicationRecord]:
        """Get an application by ID"""
        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.*, u.name as freelancer_name
                FROM applications a
                JOIN users u ON a.freelancer_id = u.user_id
                WHERE a.application_id = %s
            """, (application_id,))
            row = cursor.fetchone()
            return self._row_to_record(row) if row else None

    def set_status(self, application_id: int, new_status: str) -> Optional[ApplicationRecord]:
        """Update application status"""
        new_status = new_status.lower()
        if new_status not in STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(STATUSES)}")

        with DatabaseManager.get_cursor() as cursor:
            cursor.execute("""
                UPDATE applications
                SET status = %s
                WHERE application_id = %s
            """, (new_status, application_id))

            if cursor.rowcount == 0:
                return None

            return self.get_application(application_id)

    def _row_to_record(self, row) -> ApplicationRecord:
        """Convert database row to ApplicationRecord"""
        return ApplicationRecord(
            application_id=row['application_id'],
            job_id=row['job_id'],
            freelancer_id=row['freelancer_id'],
            freelancer_name=row['freelancer_name'],
            cover_letter=row['cover_letter'],
            status=row['status'],
            created_at=row['applied_at'] if 'applied_at' in row else datetime.now()
        )


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
    search_open_jobs()
    job_id = ask_int("Job ID you want to apply to:")
    if job_id is None:
        print_error("Job ID is required.")
        return
    cover_letter = ask_input("Add a short cover letter:")
    if len(cover_letter.strip()) < 5:
        print_error("Try to write at least a few words so the client has context.")
        return
    application = application_manager.submit(job_id, user.user_id, user.name, cover_letter)
    print_success(f"Application submitted!")


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
            search_open_jobs()
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

            # Get the application details before updating
            application = application_manager.get_application(application_id)

            updated = application_manager.set_status(application_id, new_status)
            if not updated:
                print_error("Could not find that application ID.")
            else:
                print_success(f"Application #{application_id} marked as {new_status}.")

                # Auto-create workspace and close job when application is accepted
                if new_status == "accepted" and application:
                    try:
                        # Get job details to find client_id
                        job = Job.find_by_id(application.job_id)
                        if job and job.client_id:
                            # Create workspace
                            project_id = WorkspaceManager.create_workspace(
                                application_id=application.application_id,
                                job_id=application.job_id,
                                freelancer_id=application.freelancer_id,
                                client_id=job.client_id
                            )
                            print_success(f"Workspace created! Project ID: {project_id}")
                            print_info("The freelancer can now access the workspace from the Workspace Manager menu.")

                            # Close the job so it doesn't appear in searches anymore
                            job.close()
                            print_success(f"Job '{job.title}' has been closed and removed from open job listings.")
                        else:
                            print_warning("Could not create workspace: Job or client information not found.")
                    except Exception as e:
                        print_error(f"Error creating workspace: {e}")
                        print_info("Application was accepted, but workspace creation failed.")
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
