from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, index=True, nullable=False)
    is_member = db.Column(db.Boolean, default=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_type = db.Column(db.String(64))
    target_wiki = db.Column(db.String(64))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(32), default='Planned')
    lead_organizer = db.Column(db.String(128), db.ForeignKey('users.username'), nullable=False)
    co_organizers = db.Column(db.JSON, default=list)
    is_contest = db.Column(db.Boolean, default=False)
    jury_members = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)