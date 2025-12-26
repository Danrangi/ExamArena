import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from src.config.config import Config

# Initialize globally
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    # 1. Determine Paths for .Exe vs Source
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe
        base_dir = sys._MEIPASS
        exe_dir = os.path.dirname(sys.executable)
        instance_path = os.path.join(exe_dir, 'instance')
    else:
        # Running from source code
        # FIX: Changed from '../../..' to '../..' to correctly find Project Root
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        instance_path = os.path.join(base_dir, 'instance')

    # Ensure instance folder exists
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # 2. Initialize Flask with Correct Resource Paths
    app = Flask(__name__,
                instance_path=instance_path,
                template_folder=os.path.join(base_dir, 'src/resources/templates'),
                static_folder=os.path.join(base_dir, 'src/resources/static'))

    # 3. Load Config
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_db_uri(instance_path)

    # 4. Init Extensions
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Import and Register Components
        from . import models
        from .controllers import auth, main, admin
        from .services import exam_service
        
        # Create Tables & Initial Data
        db.create_all()
        exam_service.seed_initial_data()

        # Register Blueprints
        app.register_blueprint(auth.bp)
        app.register_blueprint(main.bp)
        app.register_blueprint(admin.bp)

        # Global Request Hooks
        app.before_request(exam_service.load_user_context)
        
        return app
