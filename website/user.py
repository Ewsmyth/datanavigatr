import sqlite3
import paramiko
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
import os
from flask_login import login_required, current_user
from .models import db, IngestQuery, User, Mission, MissionMember, UserQuery, RemoteMachine
from .qdb1 import QDB1 # Import the model for the qdb1 table
from .decorators import role_required
from datetime import datetime
from .utils import translate_parameters
from .qdb1_operations import fetch_query_results 

user = Blueprint('user', __name__)

@user.route('/<username>/userhome/')
@login_required
def user_home(username):
    # Fetch missions where the user is the owner or a member
    user_missions = Mission.query.filter(
        (Mission.mission_owner == current_user.id) |  # Missions owned by the current user
        (Mission.id.in_(db.session.query(MissionMember.mission_id).filter_by(user_id=current_user.id)))
    ).all()

    # Extract the mission IDs from the user's missions to use for querying UserQuery
    mission_ids = [mission.id for mission in user_missions]

    # Fetch all UserQuery records that are associated with those mission IDs
    user_queries = UserQuery.query.filter(UserQuery.mission_id.in_(mission_ids)).all()

    # Pass both missions and user queries to the template
    return render_template('user-home.html', username=username, missions=user_missions, queries=user_queries)

@user.route('/<username>/userhome/missions/', methods=['POST'])
@login_required
@role_required('user')
def create_new_mission(username):
    # Get the form data
    mission_name = request.form.get('mission-name-fr-usr')
    mission_justification = request.form.get('mission-justification-fr-usr')
    mission_owner = current_user.id
    mission_members = request.form.getlist('mission-members')  # Use getlist() to retrieve multiple members

    # Step 1: Create and commit the new Mission
    create_mission = Mission(
        mission_name=mission_name,
        mission_justification=mission_justification,
        mission_owner=mission_owner,
    )
    db.session.add(create_mission)
    db.session.commit()  # Commit to get the generated mission_id

    # Step 2: Add the current_user to the MissionMembers table
    current_user_member = MissionMember(
        mission_id=create_mission.id,
        user_id=current_user.id,  # Add the current user as a member
        access_level='owner'      # Assign 'owner' access level to the creator
    )
    db.session.add(current_user_member)

    # Step 3: Associate other members with the mission
    if mission_members:  # Ensure there are members before iterating
        for member_username in mission_members:
            user_query = User.query.filter_by(username=member_username).first()

            if user_query:
                # Create a new MissionMember entry with the found user_id and new mission_id
                mission_member = MissionMember(
                    mission_id=create_mission.id,
                    user_id=user_query.id,  # Corrected to user_query.id, not user.id
                    access_level='full'     # You can adjust access level as needed
                )
                db.session.add(mission_member)
            else:
                # Handle case where the username doesn't exist (optional)
                flash(f"User {member_username} does not exist.", 'warning')

    # Step 4: Commit all MissionMember entries
    db.session.commit()

    # Redirect to user home after successful mission creation
    return redirect(url_for('user.user_home', username=username))

@user.route('/<username>/userhome/ingest/')
@login_required
@role_required('user')
def user_ingest(username):
    # Fetch all IngestQuery records
    queries = IngestQuery.query.all()
    remote_machines = RemoteMachine.query.filter_by(author_id=current_user.id).all()
    
    return render_template('user-ingest.html', username=username, queries=queries, remote_machines=remote_machines)

@user.route('/<username>/userhome/ingest/saveremotemachine/', methods=['POST'])
@login_required
@role_required('user')
def save_remote_machine(username):
    if current_user.username != username:
        flash('Unauthorized access', 'error')
        return redirect(url_for('auth.login'))

    remote_machine_name = request.form.get('machine_name')
    ssh_username = request.form.get('username')
    ssh_password = request.form.get('password')
    server_ip = request.form.get('ip')
    db_file_path = request.form.get('db_file_path')
    sql_query = request.form.get('sql_query')
    content_file_path = request.form.get('content_file_path')

    # Input validation
    if not (ssh_username and ssh_password and server_ip and db_file_path and sql_query):
        flash('All fields are required to save parameters', 'error')
        return redirect(url_for('user.user_ingest', username=username))
    
    # Create a new RemoteMachine entry
    new_remote_machine = RemoteMachine(
        author_id=current_user.id,
        machine_name=remote_machine_name,
        machine_username=ssh_username,
        machine_password=ssh_password,
        machine_ip=server_ip,
        machine_file_path=db_file_path,
        machine_query=sql_query
    )

    # Conditionally set content_file_path if provided
    if content_file_path:
        new_remote_machine.machine_content_file_path = content_file_path

    # Save to the database
    db.session.add(new_remote_machine)
    db.session.commit()

    # Notify user and redirect
    flash('Parameters saved successfully', 'success')
    return redirect(url_for('user.user_ingest', username=username))

@user.route('/delete_remote_machine/<int:machine_id>', methods=['DELETE'])
@login_required
@role_required('user')
def delete_remote_machine(machine_id):
    machine = RemoteMachine.query.get_or_404(machine_id)
    
    # Ensure the current user owns this machine before deleting
    if machine.author_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        db.session.delete(machine)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user.route('/<username>/userhome/new-query/', methods=['POST'])
@login_required
@role_required('user')
def user_new_query(username):
    query_author = current_user.id
    query_name = request.form.get('query-name-fr-usr')
    query_mission = request.form.get('assigned-mission-fr-usr')
    justification = request.form.get('justification-fr-usr')
    start_date = request.form.get('start-date-fr-usr')
    start_time = request.form.get('start-time-fr-usr')
    end_date = request.form.get('end-date-fr-usr')
    end_time = request.form.get('end-time-fr-usr')
    parameters = request.form.get('query-parameters-fr-usr')

    try:
        join_start_date_time = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        print(f"Error parsing start date/time: {e}")
        return redirect(url_for('user.user_home', username=username))

    try:
        join_end_date_time = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
    except ValueError as e:
        print(f"Error parsing end date/time: {e}")
        return redirect(url_for('user.user_home', username=username))

    # Translate parameters only if they are not empty
    where_clause = translate_parameters(parameters) if parameters.strip() else None

    # Create the UserQuery instance
    create_user_query = UserQuery(
        author_id=query_author,
        query_name=query_name,
        mission_id=query_mission,
        justification=justification,
        parameters=parameters,
        start_datetime=join_start_date_time,
        end_datetime=join_end_date_time
    )

    db.session.add(create_user_query)
    db.session.commit()  # Commit to get the generated query_id

    # Fetch query results using the translated or empty where_clause
    query_results = fetch_query_results(join_start_date_time, join_end_date_time, where_clause)

    # Update the total_results field with the count of results
    total_results = len(query_results)
    create_user_query.total_results = total_results

    # Commit the updated UserQuery
    db.session.commit()

    flash('New query submitted with total results calculated', 'success')
    return redirect(url_for('user.user_home', username=username))

@user.route('/<username>/userhome/ingest/ingestquery/')
@login_required
@role_required('user')
def user_ingest_query(username):
    return render_template('user-ingest-query.html', username=username)

@user.route('/<username>/userhome/ingest/createnewingestquery/', methods=['POST'])
@login_required
@role_required('user')
def user_create_new_ingest_query(username):
    query_name = request.form.get('name-fr-usr')
    query_code = request.form.get('query-fr-usr')
    query_owner = current_user.id

    # Define a directory to store SQL query files
    sql_query_dir = current_app.config.get('SQL_QUERY_DIR')
    if not sql_query_dir:
        sql_query_dir = os.path.join(os.getcwd(), 'sql_queries')
        os.makedirs(sql_query_dir, exist_ok=True)  # Ensure the directory exists

    # Create a file name for the new SQL query
    query_filename = f"{query_name.replace(' ', '_').lower()}.txt"
    query_filepath = os.path.join(sql_query_dir, query_filename)

    # Write the SQL query to the file
    with open(query_filepath, 'w') as f:
        f.write(query_code)

    # Create a new IngestQuery entry and store the file path
    create_new_query = IngestQuery(
        name=query_name,
        sql_query=query_filepath,  # Store the file path in the model
        created_by=query_owner,
        edited_by=query_owner
    )

    # Save the new query to the database
    db.session.add(create_new_query)
    db.session.commit()

    flash("Ingest Query created successfully.", "success")
    return redirect(url_for('user.user_ingest_query', username=username))

@user.route('/<username>/userhome/queries/<int:query_id>/view', methods=['GET'])
@login_required
@role_required('user')
def view_query(username, query_id):
    # Fetch missions where the user is the owner or a member
    user_missions = Mission.query.filter(
        (Mission.mission_owner == current_user.id) |
        (Mission.id.in_(db.session.query(MissionMember.mission_id).filter_by(user_id=current_user.id)))
    ).all()

    # Extract mission IDs
    mission_ids = [mission.id for mission in user_missions]

    # Fetch all UserQuery records associated with the mission IDs
    user_queries = UserQuery.query.filter(UserQuery.mission_id.in_(mission_ids)).all()

    # Fetch the specific query by query_id
    user_query = UserQuery.query.filter_by(id=query_id, author_id=current_user.id).first()

    if not user_query:
        flash('Query not found or you do not have access to it.', 'danger')
        return redirect(url_for('user.user_home', username=username))

    # Get start and end datetime
    start_datetime = user_query.start_datetime
    end_datetime = user_query.end_datetime

    # Translate parameters into SQL WHERE clause
    where_clause = translate_parameters(user_query.parameters)

    # Fetch data from qdb1 based on time range and parameters
    query_results = fetch_query_results(start_datetime, end_datetime, where_clause)

    # Extract table headers (column names) from the result set
    headers = query_results[0].keys() if query_results else []

    # Render the query results page
    return render_template(
        'user-view-query.html', 
        username=username, 
        query=user_query, 
        headers=headers, 
        results=query_results, 
        missions=user_missions, 
        queries=user_queries
    )

@user.route('/<username>/userhome/handleingest/', methods=['POST'])
@login_required
@role_required('user')
def handle_ingest(username):
    # Get the form data
    ip = request.form.get('ip')
    ssh_username = request.form.get('username')
    ssh_password = request.form.get('password')
    db_file_path = request.form.get('db_file_path')
    media_file_path = request.form.get('content_file_path')  # New input for media files
    sql_query_path = request.form.get('sql_query')  # Get the file path for the SQL query

    # Read the SQL query from the file
    with open(sql_query_path, 'r') as f:
        sql_query = f.read()

    try:
        # Run the ingestion process
        run_ssh_sql_query(ip, ssh_username, ssh_password, db_file_path, media_file_path, sql_query)
        flash("Query executed and data ingested successfully into qdb1.", "success")
    except Exception as e:
        # Log the error to the console and flash it
        print(f"Error: {str(e)}")
        flash(f"Error during data ingestion: {str(e)}", "danger")

    return redirect(url_for('user.user_ingest', username=username))


def run_ssh_sql_query(ip, ssh_username, ssh_password, db_file_path, media_file_path, sql_query):
    """Establish SSH connection, fetch .db and media files, run SQL query, and ingest data."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    conn = None

    try:
        # Connect to the remote server using SSH
        ssh.connect(hostname=ip, username=ssh_username, password=ssh_password)

        # Use SFTP to fetch the remote .db file
        sftp = ssh.open_sftp()

        # Check and download the .db file
        try:
            sftp.stat(db_file_path)  # This will raise an error if the file does not exist
        except FileNotFoundError:
            raise Exception(f"The file {db_file_path} does not exist on the remote server.")
        except PermissionError:
            raise Exception(f"Permission denied to access {db_file_path} on the remote server.")

        # Retrieve the download path from the app configuration
        local_temp_dir = current_app.config['DOWNLOADED_DB_PATH']
        local_db_path = os.path.join(local_temp_dir, os.path.basename(db_file_path))  # Temporary local copy

        # Download the .db file
        sftp.get(db_file_path, local_db_path)
        print(f"Downloaded database to {local_db_path}")

        # Check and download media files if media_file_path is provided
        if media_file_path:
            try:
                sftp.stat(media_file_path)  # Check if the directory exists
            except FileNotFoundError:
                raise Exception(f"The directory {media_file_path} does not exist on the remote server.")
            except PermissionError:
                raise Exception(f"Permission denied to access {media_file_path} on the remote server.")

            # Local media directory
            local_media_dir = os.path.join(current_app.config['DOWNLOADED_MEDIA_PATH'], os.path.basename(media_file_path))
            os.makedirs(local_media_dir, exist_ok=True)  # Ensure the directory exists

            # List and download media files
            media_files = sftp.listdir(media_file_path)
            for file in media_files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi')):  # Add other extensions as needed
                    remote_file_path = os.path.join(media_file_path, file)
                    local_file_path = os.path.join(local_media_dir, file)
                    sftp.get(remote_file_path, local_file_path)
                    print(f"Downloaded media file: {file}")

        sftp.close()

        # Connect to the downloaded .db file and run the SQL query
        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        new_data = cursor.fetchall()

        # Insert non-duplicate rows into the qdb1 table
        for row in new_data:
            # Check if this row already exists in the qdb1 table
            exists = QDB1.query.filter_by(
                TX_USER_ID=row[0],
                RX_USER_ID=row[1],
                TX_ASSOC_USRNM=row[2],
                EVENT=row[3],
                TX_ASSOC_EMAIL=row[4],
                TX_ACCT_PASSWD=row[5],
                TX_ACCT_AUTH=row[6],
                TX_CTL_BY=row[7],
                TX_ASSOC_TEAM=row[8],
                TX_ASSOC_FNAME=row[9],
                TX_ASSOC_LNAME=row[10],
                TX_ACCT_STATUS=row[11],
                TX_ASSOC_PHONE=row[12],
                LOCATION=row[13],
                FINANCE_ID=row[14],
                CONTENT_ID=row[15],
                MEDIA=row[16],
                GROUP_PARTICIPANTS=row[17],
                GROUP_CHAT_NAME=row[18],
                CONTENT=row[19],
                UP_TIME=row[20],
                INITIAL_TIME=row[21]
            ).first()

            if exists:
                # If the row already exists, skip to the next one
                # print(f"Duplicate row found, skipping: {row}")
                continue

            qdb1_record = QDB1(
                TX_USER_ID=row[0],
                RX_USER_ID=row[1],
                TX_ASSOC_USRNM=row[2],
                EVENT=row[3],
                TX_ASSOC_EMAIL=row[4],
                TX_ACCT_PASSWD=row[5],
                TX_ACCT_AUTH=row[6],
                TX_CTL_BY=row[7],
                TX_ASSOC_TEAM=row[8],
                TX_ASSOC_FNAME=row[9],
                TX_ASSOC_LNAME=row[10],
                TX_ACCT_STATUS=row[11],
                TX_ASSOC_PHONE=row[12],
                LOCATION=row[13],
                FINANCE_ID=row[14],
                CONTENT_ID=row[15],
                MEDIA=row[16],
                GROUP_PARTICIPANTS=row[17],
                GROUP_CHAT_NAME=row[18],
                CONTENT=row[19],
                UP_TIME=row[20],
                INITIAL_TIME=row[21]
            )
            db.session.add(qdb1_record)

        db.session.commit()

    except paramiko.SSHException as e:
        raise Exception(f"SSH connection error: {e}")
    except sqlite3.Error as e:
        raise Exception(f"SQL execution error: {e}")
    finally:
        if conn:
            conn.close()
        ssh.close()

@user.route('/<username>/userhome/update_account', methods=['POST'])
@login_required
@role_required('user')
def user_update_account(username):
    # Fetch the current user object
    user = User.query.filter_by(username=username).first()

    # Fetch form data
    new_username = request.form.get('new-username-fr-usr')
    new_email = request.form.get('new-email-fr-usr')
    new_password = request.form.get('new-password-fr-usr')
    confirm_password = request.form.get('confirm-new-password-fr-usr')
    new_firstname = request.form.get('new-firstname-fr-usr')
    new_lastname = request.form.get('new-lastname-fr-usr')
    new_status = request.form.get('new-status-fr-usr')
    new_theme = request.form.get('new-theme-fr-user')

    # Flag to track if we need to commit changes to the database
    changes_made = False

    # Check if any fields are being updated and update them only if they differ
    if new_username and new_username != user.username:
        user.username = new_username
        changes_made = True

    if new_email and new_email != user.email:
        user.email = new_email
        changes_made = True

    # Handle password change if provided
    if new_password:
        if new_password == confirm_password:
            user.set_password(new_password)  # Hash and update the password
            changes_made = True
        else:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('user.user_home', username=username))

    if new_firstname and new_firstname != user.firstname:
        user.firstname = new_firstname
        changes_made = True

    if new_lastname and new_lastname != user.lastname:
        user.lastname = new_lastname
        changes_made = True

    # Update account status if it has changed
    if new_status and str(user.is_active) != new_status:
        user.is_active = bool(int(new_status))  # Convert '1' or '0' to Boolean
        changes_made = True

    # Update theme if changed
    if new_theme and str(user.theme) != new_theme:
        user.theme = bool(int(new_theme))  # Convert '1' or '0' to Boolean
        changes_made = True

    # If changes were made, commit them to the database
    if changes_made:
        db.session.commit()
        flash('Your account has been updated successfully!', 'success')
    else:
        flash('No changes were made.', 'info')

    return redirect(url_for('user.user_home', username=username))

@user.route('/<username>/userhome/userhelp/')
@login_required
@role_required('user')
def user_help(username):
    return render_template('user-help.html', username=username)