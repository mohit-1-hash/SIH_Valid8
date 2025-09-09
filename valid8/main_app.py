"""
Certificate Verification System - Main Application
Database-based certificate verification (no blockchain)
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """Create and configure Flask application"""

    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/certificates.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure login manager
    login_manager.login_view = 'auth_routes.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('database', exist_ok=True)

    # Import and register blueprints
    from app.verification import verification_routes
    from app.auth import auth_routes  
    from app.admin import admin_routes

    app.register_blueprint(verification_routes.bp)
    app.register_blueprint(auth_routes.bp, url_prefix='/auth')
    app.register_blueprint(admin_routes.bp, url_prefix='/admin')

    # Import models to ensure they are registered
    from app.models import database_models

    # Create database tables
    with app.app_context():
        db.create_all()
        database_models.create_sample_data()

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.database_models import User
        return User.query.get(int(user_id))

    return app
