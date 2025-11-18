from database.db_manager import DatabaseManager


class Portfolio:
    """Portfolio model - builds portfolio from completed projects and reviews"""

    @classmethod
    def get_by_freelancer(cls, freelancer_id):
        """Get portfolio for a freelancer based on completed projects"""
        with DatabaseManager.get_cursor() as cursor:
            query = """
                SELECT
                    p.project_id,
                    p.freelancer_id,
                    p.client_id,
                    j.title,
                    j.description,
                    j.required_skills,
                    p.created_at,
                    p.completed_at,
                    r.rating,
                    r.comment as review_comment
                FROM projects p
                JOIN jobs j ON p.job_id = j.job_id
                LEFT JOIN reviews r ON p.project_id = r.project_id AND r.reviewee_id = %s
                WHERE p.freelancer_id = %s AND p.status = 'completed'
                ORDER BY p.completed_at DESC
            """
            cursor.execute(query, (freelancer_id, freelancer_id))
            return cursor.fetchall()

    @classmethod
    def get_stats(cls, freelancer_id):
        """Get portfolio statistics for a freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            stats_query = """
                SELECT
                    COUNT(p.project_id) as total_projects,
                    AVG(r.rating) as average_rating,
                    COUNT(r.review_id) as total_reviews
                FROM projects p
                LEFT JOIN reviews r ON p.project_id = r.project_id AND r.reviewee_id = %s
                WHERE p.freelancer_id = %s AND p.status = 'completed'
            """
            cursor.execute(stats_query, (freelancer_id, freelancer_id))
            return cursor.fetchone()

    @classmethod
    def get_skills_summary(cls, freelancer_id):
        """Get summary of skills from completed projects"""
        with DatabaseManager.get_cursor() as cursor:
            skills_query = """
                SELECT DISTINCT j.required_skills
                FROM projects p
                JOIN jobs j ON p.job_id = j.job_id
                WHERE p.freelancer_id = %s AND p.status = 'completed'
            """
            cursor.execute(skills_query, (freelancer_id,))
            results = cursor.fetchall()
            all_skills = []
            for row in results:
                if row['required_skills']:
                    all_skills.extend(row['required_skills'].split(','))
            return list(set(skill.strip() for skill in all_skills))

    @classmethod
    def get_reviews(cls, freelancer_id):
        """Get all reviews for a freelancer"""
        with DatabaseManager.get_cursor() as cursor:
            reviews_query = """
                SELECT
                    r.review_id,
                    r.project_id,
                    r.rating,
                    r.comment,
                    r.created_at,
                    u.name as reviewer_name
                FROM reviews r
                JOIN users u ON r.reviewer_id = u.user_id
                WHERE r.reviewee_id = %s
                ORDER BY r.created_at DESC
            """
            cursor.execute(reviews_query, (freelancer_id,))
            return cursor.fetchall()

    @classmethod
    def to_dict(cls, freelancer_id):
        """Get complete portfolio as dictionary"""
        return {
            'freelancer_id': freelancer_id,
            'projects': cls.get_by_freelancer(freelancer_id),
            'stats': cls.get_stats(freelancer_id),
            'skills': cls.get_skills_summary(freelancer_id),
            'reviews': cls.get_reviews(freelancer_id)
        }