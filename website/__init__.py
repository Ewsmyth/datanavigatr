import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from .models import db, User, IngestQuery
from flask_limiter.util import get_remote_address
from .qdb1 import QDB1
from .create_queries import create_reporter_query

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-navi-gatr-data.db'
    app.config['SQLALCHEMY_BINDS'] = {
        'qdb1': 'sqlite:///qdb1.db'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'aabbccddeeffgg'

    # Define a path to store SQL query files
    app.config['SQL_QUERY_DIR'] = os.path.join(os.getcwd(), 'sql_queries')

    # Ensure the directory exists
    os.makedirs(app.config['SQL_QUERY_DIR'], exist_ok=True)

    # Define a path to store downloaded .db files
    if os.name == 'nt':  # Windows
        app.config['DOWNLOADED_DB_PATH'] = os.path.join(os.getcwd(), 'temp')
    else:  # Unix/Linux/Mac
        app.config['DOWNLOADED_DB_PATH'] = '/tmp'

    # Ensure the directory exists
    os.makedirs(app.config['DOWNLOADED_DB_PATH'], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from .auth import auth
    from .admin import admin
    from .user import user
    from .decorators import decorators

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    app.register_blueprint(decorators)


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
                    createAdminUser.set_password('password')
                    db.session.add(createAdminUser)
                    db.session.commit()
                    print("Admin user has been created successfully.")
        except Exception as e:
            print(f"Error creating admin user: {e}")

    with app.app_context():
        db.create_all()
        createAdminUser()
        create_reporter_query()

    return app