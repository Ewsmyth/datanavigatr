import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from .models import db, User
from .create_queries import create_reporter_query

bcrypt = Bcrypt()

def create_app():
    # Initialize Flask app and load configurations from the Config class
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)
    
    # Ensure necessary directories exist, based on environment variables
    os.makedirs(app.config['SQL_QUERY_DIR'], exist_ok=True)
    os.makedirs(app.config['DOWNLOADED_DB_PATH'], exist_ok=True)
    
    # Initialize database, bcrypt, and other components
    db.init_app(app)
    bcrypt.init_app(app)

    # Configure login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    # Load user for the Flask-Login manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Set the login view for redirection when not logged in
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register Blueprints for modular application structure
    from .auth import auth
    from .admin import admin
    from .user import user
    from .decorators import decorators

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    app.register_blueprint(decorators)

    # Function to create an admin user if not exists
    def createAdminUser():
        try:
            with app.app_context():
                searchForAdmin = User.query.filter_by(auth='admin').first()
                if not searchForAdmin:
                    print("No admin user, attempting to create an admin user...")
                    createAdminUser = User(
                        username='admin',
                        email='admin@admin.com',
                        auth='admin'
                    )
                    createAdminUser.set_password(os.environ.get('ADMIN_PASSWORD', 'password'))
                    db.session.add(createAdminUser)
                    db.session.commit()
                    print("Admin user has been created successfully.")
        except Exception as e:
            print(f"Error creating admin user: {e}")

    # Initialize the database and create necessary queries
    with app.app_context():
        db.create_all()
        createAdminUser()
        create_reporter_query()

    return app
