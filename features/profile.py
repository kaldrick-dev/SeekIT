from models.user import User, get_user_by_email
from utils.display import Display

class ProfileManager:
    """Profile service to display and manage user profiles"""

    @staticmethod
    def display_profile(user):
        """Display user profile with all information"""
        if isinstance(user, dict):
            user_data = user
        else:
            user_data = {
                'name': user.name,
                'email': user.email,
                'location': user.location,
                'user_type': user.user_type,
                'created_at': user.created_at
            }

        Display.print_user_profile(user_data)

        if hasattr(user, 'skills') and user.skills:
            ProfileManager.display_skills(user.skills)

    @staticmethod
    def display_skills(skills):
        """Display user skills in a formatted way"""
        if not skills:
            Display.print_warning("No skills listed")
            return

        skill_list = []
        for skill in skills:
            if isinstance(skill, dict):
                skill_list.append(skill)
            elif isinstance(skill, str):
                skill_list.append({'skill_name': skill, 'skill_level': 'N/A'})
            else:
                skill_list.append({'skill_name': str(skill), 'skill_level': 'N/A'})

        Display.print_skills(skill_list)

    @staticmethod
    def display_full_profile(user_id=None, email=None):
        """Display complete user profile by user_id or email"""
        user = None

        if email:
            user = get_user_by_email(email)

        if not user:
            Display.print_error("User not found")
            return

        ProfileManager.display_profile(user)

    @staticmethod
    def show_profile_menu(user):
        """Show profile management menu"""
        Display.print_menu(
            "Profile Management",
            [
                ("1", "View Full Profile"),
                ("2", "View Skills"),
                ("3", "Update Profile (Coming Soon)"),
                ("4", "Manage Skills (Coming Soon)")
            ]
        )
