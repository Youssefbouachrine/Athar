from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False, index=True)
    is_member = db.Column(db.Boolean, default=True, nullable=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    snapshots = db.relationship("StatSnapshot", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} member={self.is_member}>"


class StatSnapshot(db.Model):
    __tablename__ = "stat_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_edits = db.Column(db.Integer, default=0, nullable=False)
    home_wiki = db.Column(db.String(64), default="ar.wikipedia.org")
    wiki_breakdown = db.Column(db.JSON, nullable=True)  # {"ar.wikipedia": 120, "commons": 45}
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<StatSnapshot user_id={self.user_id} edits={self.total_edits}>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)  # Bleach sanitized HTML
    project_type = db.Column(db.String(64), default="Workshop", nullable=False)
    target_wiki = db.Column(db.String(64), default="ar.wikipedia.org", nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(32), default="In Progress", nullable=False)  # Planned, In Progress, Completed

    # Ownership & Roles
    lead_organizer = db.Column(db.String(128), nullable=False)
    co_organizers = db.Column(db.JSON, nullable=True)  # ["UserA", "UserB"]
    is_contest = db.Column(db.Boolean, default=False, nullable=False)
    jury_members = db.Column(db.JSON, nullable=True)   # ["Jury1", "Jury2"]

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "project_type": self.project_type,
            "target_wiki": self.target_wiki,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
            "lead_organizer": self.lead_organizer,
            "co_organizers": self.co_organizers or [],
            "is_contest": self.is_contest,
            "jury_members": self.jury_members or [],
            "created_at": self.created_at.isoformat()
        }