from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .decorators import role_required
from .models import db, User
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__)

@admin.route('/<username>/adminhome/')
@login_required
@role_required('admin')
def admin_home(username):
    return render_template('admin-home.html', username=username)

@admin.route('/<username>/adminhome/users/')
@login_required
@role_required('admin')
def admin_users(username):
    users = User.query.all()

    return render_template('admin-users.html', username=username, users=users)

@admin.route('/<username>/adminhome/users/edituser/<int:user_id>/', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_user(username, user_id):
    user_to_edit = User.query.get_or_404(user_id)

    return render_template('admin-edit-user.html', username=username, user_to_edit=user_to_edit)

@admin.route('/<username>/adminhome/users/createuser/', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_user(username):
    new_username = request.form.get('username-fr-user')
    new_email = request.form.get('email-fr-user')
    new_password = request.form.get('password-fr-user')
    authority = request.form.get('authority-fr-user')

    # Check if the username or email are already used in the database
    user_exists = User.query.filter((User.username == new_username) | (User.email == new_email)).first()

    if user_exists:
        flash('The username or email you entered already belongs to a user.', 'warning')
        return redirect(url_for('admin.admin_create_user', username=username))

    # Create new user
    create_user = User(
        username=new_username,
        email=new_email,
        auth=authority
    )
    create_user.set_password(new_password)
    db.session.add(create_user)
    print(f'{current_user.username} created new user: {new_username}.')

    db.session.commit()

    flash('New user has been created.')
    return redirect(url_for('admin.admin_users', username=username))

@admin.route('/<username>/edit-user/<int:user_id>/', methods=['POST'])
@login_required
@role_required('admin')
def update_user_info(username, user_id):
    changing_user = User.query.get_or_404(user_id)

    updated_username = request.form.get('username-fr-user')
    updated_email = request.form.get('email-fr-user')
    updated_password = request.form.get('password-fr-user')
    updated_auth = request.form.get('auth-fr-user')
    updated_firstname = request.form.get('firstname-fr-user')
    updated_lastname = request.form.get('lastname-fr-user')
    updated_status = request.form.get('status-fr-user')
    updated_theme = request.form.get('theme-fr-user')

    if updated_username and updated_username != changing_user.username:
        changing_user.username = updated_username

    if updated_email and updated_email != changing_user.email:
        changing_user.email = updated_email

    if updated_password:
        changing_user.password = generate_password_hash(updated_password)

    if updated_auth and updated_auth != changing_user.auth:
        changing_user.auth = updated_auth

    if updated_firstname and updated_firstname != changing_user.firstname:
        changing_user.firstname = updated_firstname

    if updated_lastname and updated_lastname != changing_user.lastname:
        changing_user.lastname = updated_lastname

    changing_user.is_active = True if updated_status == 'True' else False

    changing_user.theme = True if updated_theme =='True' else False

    db.session.commit()

    return redirect(url_for('admin.admin_edit_user', username=username, user_id=user_id))