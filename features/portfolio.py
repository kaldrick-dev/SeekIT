from database.db_manager import DatabaseManager
from models.portfolio import Portfolio
from utils.display import Display

class PortfolioManager:
    """Portfolio service to manage project display and completions"""

    @staticmethod
    def display_portfolio(freelancer_id):
        """Display complete portfolio for a freelancer"""
        portfolio_data = Portfolio.to_dict(freelancer_id)

        if not portfolio_data:
            Display.print_error("Could not load portfolio")
            return

        Display.print_header("FREELANCER PORTFOLIO")

        PortfolioManager.display_stats(portfolio_data.get('stats'))
        PortfolioManager.display_skills(portfolio_data.get('skills'))
        PortfolioManager.display_projects(portfolio_data.get('projects'))
        PortfolioManager.display_reviews(portfolio_data.get('reviews'))

    @staticmethod
    def display_stats(stats):
        """Display portfolio statistics"""
        if not stats:
            Display.print_warning("No statistics available")
            return

        stats_dict = {
            'Total Completed Projects': stats.get('total_projects', 0),
            'Average Rating': f"{stats.get('average_rating', 0):.1f} / 5.0" if stats.get('average_rating') else 'N/A',
            'Total Reviews': stats.get('total_reviews', 0)
        }

        Display.print_stats("Portfolio Statistics", stats_dict)

    @staticmethod
    def display_skills(skills):
        """Display skills from completed projects"""
        if not skills:
            Display.print_warning("No skills to display")
            return

        Display.print_subheader("Skills & Expertise")

        skill_list = [{'skill_name': skill, 'skill_level': 'Demonstrated'} for skill in skills]
        Display.print_skills(skill_list)

    @staticmethod
    def display_projects(projects):
        """Display completed projects"""
        if not projects:
            Display.print_warning("No completed projects to display")
            return

        Display.print_subheader("Completed Projects")

        for project in projects:
            PortfolioManager.print_project_card(project)

    @staticmethod
    def print_project_card(project):
        """Print a formatted project card"""
        project_id = project.get('project_id', 'N/A')
        title = project.get('title', 'Untitled Project')
        description = project.get('description', 'No description available')
        skills = project.get('required_skills', 'None specified')
        completed_at = project.get('completed_at', 'N/A')
        rating = project.get('rating')
        review_comment = project.get('review_comment')

        print("\n" + "+" + "-" * 78 + "+")
        print(f"| {Display.color_text(f'Project: {title}', 'cyan', bold=True):<87}|")
        print("+" + "-" * 78 + "+")

        desc_lines = Display._wrap_text(description, 74)
        for line in desc_lines[:3]:
            print(f"| {line:<76} |")
        if len(desc_lines) > 3:
            print(f"| {Display.color_text('...', 'gray'):<85}|")

        print("+" + "-" * 78 + "+")
        print(f"| {Display.color_text('Skills Used:', 'yellow')} {skills}".ljust(87) + "|")
        print(f"| {Display.color_text('Completed:', 'yellow')} {completed_at}".ljust(87) + "|")

        if rating:
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            print(f"| {Display.color_text('Rating:', 'yellow')} {Display.color_text(stars, 'green')} ({rating}/5)".ljust(96) + "|")

        if review_comment:
            print("+" + "-" * 78 + "+")
            print(f"| {Display.color_text('Client Review:', 'magenta', bold=True):<87}|")
            review_lines = Display._wrap_text(review_comment, 74)
            for line in review_lines[:2]:
                print(f"| {line:<76} |")
            if len(review_lines) > 2:
                print(f"| {Display.color_text('...', 'gray'):<85}|")

        print("+" + "-" * 78 + "+\n")

    @staticmethod
    def display_reviews(reviews):
        """Display all client reviews"""
        if not reviews:
            Display.print_info("No reviews yet")
            return

        Display.print_subheader("Client Reviews")

        for review in reviews:
            PortfolioManager.print_review_card(review)

    @staticmethod
    def print_review_card(review):
        """Print a formatted review card"""
        reviewer_name = review.get('reviewer_name', 'Anonymous')
        rating = review.get('rating', 0)
        comment = review.get('comment', '')
        created_at = review.get('created_at', 'N/A')

        stars = "★" * int(rating) + "☆" * (5 - int(rating))

        print("\n" + "┌" + "─" * 78 + "┐")
        print(f"│ {Display.color_text(reviewer_name, 'cyan', bold=True):<87}│")
        print(f"│ {Display.color_text(stars, 'green')} ({rating}/5) - {created_at}".ljust(87) + "│")
        print("├" + "─" * 78 + "┤")

        if comment:
            comment_lines = Display._wrap_text(comment, 74)
            for line in comment_lines:
                print(f"│ {line:<76} │")
        else:
            print(f"│ {Display.color_text('No comment provided', 'gray'):<85}│")

        print("└" + "─" * 78 + "┘\n")

    @staticmethod
    def show_portfolio_menu():
        """Show portfolio management menu"""
        Display.print_menu(
            "Portfolio Management",
            [
                ("1", "View Full Portfolio"),
                ("2", "View Statistics"),
                ("3", "View Projects"),
                ("4", "View Reviews"),
                ("5", "Export Portfolio (Coming Soon)")
            ]
        )

    @staticmethod
    def display_portfolio_summary(freelancer_id):
        """Display a summary view of the portfolio"""
        stats = Portfolio.get_stats(freelancer_id)

        if not stats:
            Display.print_warning("No portfolio data available")
            return

        Display.print_subheader("Portfolio Summary")

        print(f"  {Display.color_text('Completed Projects:', 'cyan')} {stats.get('total_projects', 0)}")

        if stats.get('average_rating'):
            avg_rating = stats.get('average_rating')
            stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))
            print(f"  {Display.color_text('Average Rating:', 'cyan')} {Display.color_text(stars, 'green')} ({avg_rating:.1f}/5)")
        else:
            print(f"  {Display.color_text('Average Rating:', 'cyan')} Not yet rated")

        print(f"  {Display.color_text('Total Reviews:', 'cyan')} {stats.get('total_reviews', 0)}")
        print()

