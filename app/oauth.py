import os
from functools import wraps
from flask import Blueprint, session, redirect, url_for, request, abort, current_app

oauth_bp = Blueprint("oauth", __name__)

def is_mock_enabled():
    return os.getenv("MOCK_AUTH", "False").lower() in ("true", "1", "yes")

def get_current_user():
    # Development bypass: Auto-inject test user if MOCK_AUTH is enabled
    if is_mock_enabled() and "username" not in session:
        session["username"] = os.getenv("MOCK_USERNAME", "MoroccoVolunteer")
        session["is_member"] = True
    return session.get("username")

def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = get_current_user()
        if not username:
            return redirect(url_for("oauth.login"))
        if not session.get("is_member", False):
            abort(403, description="Access restricted to verified community members.")
        return f(*args, **kwargs)
    return decorated_function

def project_editor_required(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        from app.models import Project
        project = Project.query.get_or_404(project_id)
        current_user = get_current_user()
        if not current_user:
            return redirect(url_for("oauth.login"))

        co_orgs = project.co_organizers or []
        if current_user != project.lead_organizer and current_user not in co_orgs:
            abort(403, description="Only the lead organizer or co-organizers can edit this project.")
        return f(project_id, *args, **kwargs)
    return decorated_function

@oauth_bp.route("/login")
def login():
    if is_mock_enabled():
        session["username"] = os.getenv("MOCK_USERNAME", "MoroccoVolunteer")
        session["is_member"] = True
        return redirect(url_for("web.dashboard"))
    # In live mode (Student 2 will plug Authlib redirect here on Day 2)
    return redirect("https://meta.wikimedia.org/w/index.php?title=Special:OAuth/authorize")

@oauth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("web.dashboard"))

@oauth_bp.route("/oauth/callback")
def callback():
    # Placeholder for live Wikimedia token exchange (Day 2)
    session["username"] = "MoroccoVolunteer"
    session["is_member"] = True
    return redirect(url_for("web.dashboard"))
