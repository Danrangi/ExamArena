import os

class Config:
    """Application configuration."""
    # Ensure DB is saved in the instance folder properly
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ADMIN credentials
    ADMIN_USERNAME = 'EXAMARENA'
    ADMIN_PASSWORD = 'AdminArena123'

    # Secret key
    SECRET_KEY = 'Danrangi@2025'
    
    @staticmethod
    def get_db_uri(instance_path):
        return f"sqlite:///{os.path.join(instance_path, 'exam_data.db')}"
