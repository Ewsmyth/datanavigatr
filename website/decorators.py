from functools import wraps
from flask import abort, Blueprint
from flask_login import current_user

decorators = Blueprint('decorators', __name__)

def role_required(role):
    """
    Custom decorator to check if the logged-in user has the required role.
    :param role: The role required to access the route (e.g., 'admin' or 'user').
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.auth != role:
                # If the user is not authenticated or doesn't have the correct role, return a 403 Forbidden error.
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
