"""Test script for display utilities"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.display import Display

def test_basic_displays():
    """Test basic display functions"""
    Display.print_welcome_banner()
    Display.pause()

    Display.clear_screen()
    Display.print_header("Testing Display Utilities")

    # Test messages
    Display.print_success("This is a success message")
    Display.print_error("This is an error message")
    Display.print_warning("This is a warning message")
    Display.print_info("This is an info message")
    Display.print_divider()

def test_menu():
    """Test menu display"""
    Display.print_menu(
        "Main Menu",
        [
            ("1", "Search Jobs"),
            ("2", "View Applications"),
            ("3", "Manage Portfolio"),
            ("4", "Profile Settings")
        ]
    )

def test_table():
    """Test table display"""
    Display.print_subheader("Sample Job Listings")
    headers = ["ID", "Title", "Budget", "Status"]
    rows = [
        ["1", "Web Developer Needed", "$500 - $1000", "Open"],
        ["2", "Logo Design", "$200 - $400", "Open"],
        ["3", "Content Writer", "$300 - $600", "Closed"]
    ]
    Display.print_table(headers, rows)

def test_job_card():
    """Test job card display"""
    sample_job = {
        'job_id': 1,
        'title': 'Full Stack Web Developer',
        'description': 'Looking for an experienced full stack developer to build a modern web application using React and Node.js. Must have experience with databases and API development.',
        'budget_min': 1500.00,
        'budget_max': 3000.00,
        'deadline': '2025-12-31',
        'status': 'open',
        'required_skills': 'React, Node.js, MongoDB, REST APIs'
    }
    Display.print_job_card(sample_job)

def test_application_card():
    """Test application card display"""
    sample_app = {
        'application_id': 5,
        'job_id': 1,
        'status': 'pending',
        'applied_at': '2025-11-15 10:30:00',
        'cover_letter': 'I am very interested in this position and believe my 5 years of experience in full stack development makes me an ideal candidate.'
    }
    Display.print_application_card(sample_app, job_title="Full Stack Web Developer")

def test_user_profile():
    """Test user profile display"""
    sample_user = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'location': 'New York, USA',
        'user_type': 'freelancer',
        'created_at': '2025-01-15'
    }
    Display.print_user_profile(sample_user)

def test_skills():
    """Test skills display"""
    sample_skills = [
        {'skill_name': 'Python', 'skill_level': 'Expert'},
        {'skill_name': 'JavaScript', 'skill_level': 'Advanced'},
        {'skill_name': 'React', 'skill_level': 'Intermediate'},
        {'skill_name': 'Docker', 'skill_level': 'Beginner'}
    ]
    Display.print_skills(sample_skills)

def test_stats():
    """Test statistics display"""
    sample_stats = {
        'Total Jobs Posted': 45,
        'Active Applications': 12,
        'Completed Projects': 8,
        'Success Rate': '89%'
    }
    Display.print_stats("User Statistics", sample_stats)

def test_inputs():
    """Test input functions"""
    Display.print_subheader("Testing Input Functions")

    name = Display.get_input("Enter your name:")
    Display.print_success(f"Hello, {name}!")

    if Display.get_confirmation("Do you want to continue testing?"):
        Display.print_info("Continuing tests...")
    else:
        Display.print_warning("Skipping remaining tests")

def main():
    """Run all tests"""
    try:
        test_basic_displays()
        test_menu()
        Display.pause()

        Display.clear_screen()
        test_table()
        Display.pause()

        Display.clear_screen()
        test_job_card()
        Display.pause()

        Display.clear_screen()
        test_application_card()
        Display.pause()

        Display.clear_screen()
        test_user_profile()
        test_skills()
        Display.pause()

        Display.clear_screen()
        test_stats()
        Display.pause()

        Display.clear_screen()
        test_inputs()

        Display.print_success("\nAll display tests completed!")

    except KeyboardInterrupt:
        Display.print_warning("\n\nTests interrupted by user")
    except Exception as e:
        Display.print_error(f"\nError during testing: {e}")

if __name__ == "__main__":
    main()
