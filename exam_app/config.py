class Config:
    """Application configuration."""
    # Keep the existing SQLite DB path
    SQLALCHEMY_DATABASE_URI = 'sqlite:///exam_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ADMIN credentials (move from app.py)
    ADMIN_USERNAME = 'EPS'
    ADMIN_PASSWORD = 'AdminEPS123'

    # Secret key used by Flask for sessions
    SECRET_KEY = 'Danrangi@2025'
