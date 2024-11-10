from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    auth = db.Column(db.String(20), nullable=False, default='user')
    firstname = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    theme = db.Column(db.Boolean(), nullable=False, default=False)
    profile_pic = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Changed lazy='True' to lazy='select'
    users_missions = db.relationship('Mission', backref='owner', lazy='select')
    member_of = db.relationship('MissionMember', backref='mission_access', lazy='select')
    author_of = db.relationship('UserQuery', backref='query_author', lazy='select')
    remote_machines = db.relationship('RemoteMachine', backref='author', lazy='select')


class Mission(db.Model):
    __tablename__ = 'mission'
    id = db.Column(db.Integer, primary_key=True)
    mission_name = db.Column(db.String(255), nullable=False, default='New Mission')
    total_results = db.Column(db.Integer)
    mission_justification = db.Column(db.String(1000))
    mission_owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Changed lazy='True' to lazy='select'
    mission_members = db.relationship('MissionMember', backref='list_of_members', lazy='select')
    querys_mission = db.relationship('UserQuery', backref='mission_for_query', lazy='select')

class MissionMember(db.Model):
    __tablename__ = 'mission_member'
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    access_level = db.Column(db.String(40))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IngestQuery(db.Model):
    __tablename__ = 'ingest_query'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sql_query = db.Column(db.String(1000), nullable=False)  # File path to the SQL query .txt file
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    edited_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    machines = db.relationship('RemoteMachine', backref='ingest_query', lazy='select')

class UserQuery(db.Model):
    __tablename__ = 'user_query'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    query_name = db.Column(db.String(255), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('mission.id'))
    justification = db.Column(db.String(1000), nullable=False)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_results = db.Column(db.Integer)
    parameters = db.Column(db.String(1000), nullable=False)

class RemoteMachine(db.Model):
    __tablename__ = 'remote_machine'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    machine_name = db.Column(db.String(255), default='New Machine')
    machine_username = db.Column(db.String(255))
    machine_password = db.Column(db.String(1000))
    machine_ip = db.Column(db.String(255))
    machine_file_path = db.Column(db.String(255))
    machine_query = db.Column(db.Integer, db.ForeignKey('ingest_query.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
