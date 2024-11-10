from flask import Flask, Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

auth = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(min=5, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

@auth.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Rate limiting to prevent brute-force attacks
def auth_login():
    if current_user.is_authenticated:
        # Redirect to the correct dashboard based on user's role
        if current_user.auth == 'admin':
            return redirect(url_for('admin.admin_home', username=current_user.username))
        elif current_user.auth == 'user':
            return redirect(url_for('user.user_home', username=current_user.username))
        else:
            return redirect(url_for('auth.auth_login'))

    form = LoginForm()
    user = None  # Initialize user as None to avoid UnboundLocalError
    if form.validate_on_submit():
        # Fetch user by either email or username
        user = User.query.filter((User.email == form.username.data) | (User.username == form.username.data)).first()

        # Check if user exists and password matches
        if user and user.check_password(form.password.data):
            # Check if the account is active
            if not user.is_active:
                # Account is deactivated
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('auth.auth_login'))  # Redirect to the login page
            
            # Log in the user if the account is active
            login_user(user)
            flash('Login successful!', 'success')

            # Redirect based on the user's authority
            if user.auth == 'admin':
                return redirect(url_for('admin.admin_home', username=user.username))  # Admin home
            elif user.auth == 'user':
                return redirect(url_for('user.user_home', username=user.username))  # User home
            else:
                flash('Invalid authority', 'danger')  # Flash message for invalid role
                return redirect(url_for('auth.auth_login'))

        else:
            flash('Invalid username or password', 'danger')

    # Pass None as username if user is not logged in or not found
    return render_template('auth-login.html', form=form, username=None if not user else user.username)

@auth.route('/logout')
@login_required
def auth_logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.auth_login'))