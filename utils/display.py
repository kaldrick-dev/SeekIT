import os
import sys

class Display:
    """Display utilities for consistent CLI interface"""

    # Color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'gray': '\033[90m'
    }

    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    @staticmethod
    def color_text(text, color='reset', bold=False):
        """Apply color to text"""
        color_code = Display.COLORS.get(color, Display.COLORS['reset'])
        bold_code = Display.COLORS['bold'] if bold else ''
        reset = Display.COLORS['reset']
        return f"{bold_code}{color_code}{text}{reset}"

    @staticmethod
    def print_header(text, color='cyan', width=80):
        """Print a formatted header"""
        print("\n" + "=" * width)
        print(Display.color_text(text.center(width), color, bold=True))
        print("=" * width + "\n")

    @staticmethod
    def print_subheader(text, color='blue'):
        """Print a formatted subheader"""
        print("\n" + Display.color_text(f"--- {text} ---", color, bold=True) + "\n")

    @staticmethod
    def print_success(message):
        """Print success message"""
        print(Display.color_text(f"✓ {message}", 'green', bold=True))

    @staticmethod
    def print_error(message):
        """Print error message"""
        print(Display.color_text(f"✗ {message}", 'red', bold=True))

    @staticmethod
    def print_warning(message):
        """Print warning message"""
        print(Display.color_text(f"⚠ {message}", 'yellow', bold=True))

    @staticmethod
    def print_info(message):
        """Print info message"""
        print(Display.color_text(f"ℹ {message}", 'blue'))

    @staticmethod
    def print_divider(width=80, char='-'):
        """Print a divider line"""
        print(char * width)

    @staticmethod
    def print_menu(title, options, show_back=True):
        """
        Print a formatted menu

        Args:
            title: Menu title
            options: List of tuples (key, description)
            show_back: Whether to show back/exit option
        """
        Display.print_subheader(title)
        for key, description in options:
            print(f"  {Display.color_text(key, 'cyan', bold=True)}. {description}")

        if show_back:
            print(f"  {Display.color_text('0', 'yellow', bold=True)}. Back / Exit")
        print()

    @staticmethod
    def print_table(headers, rows, column_widths=None):
        """
        Print data in table format

        Args:
            headers: List of column headers
            rows: List of row data (list of lists)
            column_widths: Optional list of column widths
        """
        if not rows:
            Display.print_warning("No data to display")
            return

        # Calculate column widths if not provided
        if column_widths is None:
            column_widths = [len(str(h)) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(column_widths):
                        column_widths[i] = max(column_widths[i], len(str(cell)))

        # Print header
        header_line = " | ".join(
            Display.color_text(str(h).ljust(w), 'cyan', bold=True)
            for h, w in zip(headers, column_widths)
        )
        print("\n" + header_line)
        print("-" * (sum(column_widths) + 3 * (len(headers) - 1)))

        # Print rows
        for row in rows:
            row_line = " | ".join(
                str(cell).ljust(w)
                for cell, w in zip(row, column_widths)
            )
            print(row_line)
        print()

    @staticmethod
    def print_job_card(job):
        """
        Print a formatted job card

        Args:
            job: Job object or dictionary
        """
        if isinstance(job, dict):
            job_id = job.get('job_id', 'N/A')
            title = job.get('title', 'Untitled')
            description = job.get('description', 'No description')
            budget_min = job.get('budget_min', 0)
            budget_max = job.get('budget_max', 0)
            deadline = job.get('deadline', 'N/A')
            status = job.get('status', 'unknown')
            skills = job.get('required_skills', 'None')
        else:
            job_id = job.job_id
            title = job.title
            description = job.description
            budget_min = job.budget_min
            budget_max = job.budget_max
            deadline = job.deadline
            status = job.status
            skills = job.required_skills

        print("\n" + "+" + "-" * 78 + "+")
        print(f"| {Display.color_text(f'Job #{job_id}: {title}', 'cyan', bold=True):<87}|")
        print("+" + "-" * 78 + "+")

        # Description (truncate if too long)
        desc_lines = Display._wrap_text(description, 74)
        for line in desc_lines[:3]:  # Show first 3 lines
            print(f"| {line:<76} |")
        if len(desc_lines) > 3:
            print(f"| {Display.color_text('...', 'gray'):<85}|")

        print("+" + "-" * 78 + "+")
        print(f"| {Display.color_text('Budget:', 'yellow')} ${budget_min:.2f} - ${budget_max:.2f}".ljust(87) + "|")
        print(f"| {Display.color_text('Deadline:', 'yellow')} {deadline}".ljust(87) + "|")
        print(f"| {Display.color_text('Status:', 'yellow')} {Display._get_status_text(status)}".ljust(100) + "|")
        print(f"| {Display.color_text('Skills:', 'yellow')} {skills}".ljust(87) + "|")
        print("+" + "-" * 78 + "+\n")

    @staticmethod
    def print_application_card(application, job_title=None):
        """Print a formatted application card"""
        if isinstance(application, dict):
            app_id = application.get('application_id', 'N/A')
            job_id = application.get('job_id', 'N/A')
            status = application.get('status', 'unknown')
            applied_at = application.get('applied_at', 'N/A')
            cover_letter = application.get('cover_letter', '')
        else:
            app_id = application.application_id
            job_id = application.job_id
            status = application.status
            applied_at = application.applied_at
            cover_letter = application.cover_letter

        print("\n" + "+" + "-" * 78 + "+")
        title = f"Application #{app_id} - Job #{job_id}"
        if job_title:
            title += f": {job_title}"
        print(f"| {Display.color_text(title, 'magenta', bold=True):<87}|")
        print("+" + "-" * 78 + "+")
        print(f"| {Display.color_text('Status:', 'yellow')} {Display._get_status_text(status)}".ljust(95) + "|")
        print(f"| {Display.color_text('Applied:', 'yellow')} {applied_at}".ljust(87) + "|")

        if cover_letter:
            print("+" + "-" * 78 + "+")
            cover_lines = Display._wrap_text(cover_letter, 74)
            for line in cover_lines[:2]:  # Show first 2 lines
                print(f"| {line:<76} |")
            if len(cover_lines) > 2:
                print(f"| {Display.color_text('...', 'gray'):<85}|")

        print("+" + "-" * 78 + "+\n")

    @staticmethod
    def print_user_profile(user):
        """Print user profile information"""
        if isinstance(user, dict):
            name = user.get('name', 'Unknown')
            email = user.get('email', 'N/A')
            location = user.get('location', 'N/A')
            user_type = user.get('user_type', 'N/A')
            created_at = user.get('created_at', 'N/A')
        else:
            name = user.name
            email = user.email
            location = user.location
            user_type = user.user_type
            created_at = user.created_at

        Display.print_subheader("User Profile")
        print(f"{Display.color_text('Name:', 'cyan', bold=True)} {name}")
        print(f"{Display.color_text('Email:', 'cyan', bold=True)} {email}")
        print(f"{Display.color_text('Location:', 'cyan', bold=True)} {location}")
        print(f"{Display.color_text('User Type:', 'cyan', bold=True)} {user_type.capitalize()}")
        print(f"{Display.color_text('Member Since:', 'cyan', bold=True)} {created_at}")
        print()

    @staticmethod
    def print_skills(skills):
        """Print skills in a formatted way"""
        if not skills:
            Display.print_warning("No skills listed")
            return

        Display.print_subheader("Skills")
        for skill in skills:
            if isinstance(skill, dict):
                skill_name = skill.get('skill_name', 'Unknown')
                skill_level = skill.get('skill_level', 'N/A')
            else:
                skill_name = skill[0] if isinstance(skill, tuple) else skill
                skill_level = skill[1] if isinstance(skill, tuple) and len(skill) > 1 else 'N/A'

            level_color = Display._get_skill_level_color(skill_level)
            print(f"  • {Display.color_text(skill_name, 'white', bold=True)}: "
                  f"{Display.color_text(skill_level, level_color)}")
        print()

    @staticmethod
    def print_welcome_banner():
        """Print welcome banner"""
        Display.clear_screen()
        banner = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║               ███████╗███████╗███████╗██╗  ██╗██╗████████╗                 ║
║               ██╔════╝██╔════╝██╔════╝██║ ██╔╝██║╚══██╔══╝                 ║
║               ███████╗█████╗  █████╗  █████╔╝ ██║   ██║                    ║
║               ╚════██║██╔══╝  ██╔══╝  ██╔═██╗ ██║   ██║                    ║
║               ███████║███████╗███████╗██║  ██╗██║   ██║                    ║
║               ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝                    ║
║                                                                            ║
║                Your Gateway to Freelance Opportunities                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """
        print(Display.color_text(banner, 'cyan', bold=True))

    @staticmethod
    def get_input(prompt, color='cyan'):
        """Get user input with colored prompt"""
        colored_prompt = Display.color_text(prompt, color, bold=True)
        return input(f"{colored_prompt} ").strip()

    @staticmethod
    def get_confirmation(message):
        """Get yes/no confirmation from user"""
        response = Display.get_input(f"{message} (y/n):", 'yellow').lower()
        return response in ['y', 'yes']

    @staticmethod
    def pause():
        """Pause and wait for user to press enter"""
        input(Display.color_text("\nPress Enter to continue...", 'gray'))

    @staticmethod
    def show_loading(message="Processing"):
        """Show loading message"""
        sys.stdout.write(Display.color_text(f"{message}...", 'yellow'))
        sys.stdout.flush()

    @staticmethod
    def clear_loading():
        """Clear loading message"""
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()

    @staticmethod
    def _wrap_text(text, width):
        """Wrap text to specified width"""
        if not text:
            return ['']

        words = str(text).split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else ['']

    @staticmethod
    def _get_status_text(status):
        """Get colored status text"""
        status_colors = {
            'open': ('OPEN', 'green'),
            'closed': ('CLOSED', 'red'),
            'in_progress': ('IN PROGRESS', 'yellow'),
            'pending': ('PENDING', 'yellow'),
            'accepted': ('ACCEPTED', 'green'),
            'rejected': ('REJECTED', 'red'),
            'active': ('ACTIVE', 'green'),
            'completed': ('COMPLETED', 'blue')
        }

        text, color = status_colors.get(status.lower(), (status.upper(), 'white'))
        return Display.color_text(text, color, bold=True)

    @staticmethod
    def _get_skill_level_color(level):
        """Get color for skill level"""
        level_lower = str(level).lower()
        if level_lower in ['expert', 'advanced']:
            return 'green'
        elif level_lower in ['intermediate', 'medium']:
            return 'yellow'
        elif level_lower in ['beginner', 'basic']:
            return 'cyan'
        else:
            return 'white'

    @staticmethod
    def print_stats(title, stats):
        """
        Print statistics in a formatted way

        Args:
            title: Stats section title
            stats: Dictionary of stat_name: stat_value
        """
        Display.print_subheader(title)
        for key, value in stats.items():
            print(f"  {Display.color_text(key + ':', 'cyan', bold=True)} {value}")
        print()

    @staticmethod
    def ask_input(prompt, allow_empty=False):
        """
        Get user input with colored prompt

        Args:
            prompt: The prompt text
            allow_empty: Whether to allow empty input

        Returns:
            User input as string
        """
        while True:
            value = Display.get_input(prompt)
            if value or allow_empty:
                return value
            Display.print_warning("This field cannot be empty. Please try again.")

    @staticmethod
    def divider(width=80, char='─'):
        """Print a divider line"""
        print(char * width)

    @staticmethod
    def print_heading(text, width=80):
        """Print a formatted heading (alias for print_header)"""
        Display.print_header(text, width=width)

    @staticmethod
    def ask_int(prompt, min_value=None, max_value=None):
        """
        Get integer input from user with validation

        Args:
            prompt: The prompt text
            min_value: Optional minimum value
            max_value: Optional maximum value

        Returns:
            Integer value
        """
        while True:
            value = Display.get_input(prompt)
            try:
                int_value = int(value)
                if min_value is not None and int_value < min_value:
                    Display.print_warning(f"Value must be at least {min_value}")
                    continue
                if max_value is not None and int_value > max_value:
                    Display.print_warning(f"Value must be at most {max_value}")
                    continue
                return int_value
            except ValueError:
                Display.print_warning("Please enter a valid number")


# Module-level functions for backward compatibility
def ask_input(prompt, allow_empty=False):
    """Get user input with colored prompt (module-level alias)"""
    return Display.ask_input(prompt, allow_empty)


def divider(width=80, char='─'):
    """Print a divider line (module-level alias)"""
    Display.divider(width, char)


def print_heading(text, width=80):
    """Print a formatted heading (module-level alias)"""
    Display.print_heading(text, width)


def print_info(message):
    """Print info message (module-level alias)"""
    Display.print_info(message)


def print_success(message):
    """Print success message (module-level alias)"""
    Display.print_success(message)


def print_error(message):
    """Print error message (module-level alias)"""
    Display.print_error(message)


def print_warning(message):
    """Print warning message (module-level alias)"""
    Display.print_warning(message)


def ask_int(prompt, min_value=None, max_value=None):
    """Get integer input with validation (module-level alias)"""
    return Display.ask_int(prompt, min_value, max_value)


def print_table(headers, rows, column_widths=None):
    """Print data in table format (module-level alias)"""
    Display.print_table(headers, rows, column_widths)


def print_menu(title, options, show_back=True):
    """Print a formatted menu (module-level alias)"""
    Display.print_menu(title, options, show_back)
