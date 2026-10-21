from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Project, User, StatSnapshot
from app.oauth import member_required, project_editor_required, get_current_user
from app import db
import bleach

web_bp = Blueprint("web", __name__)

@web_bp.route("/")
def dashboard():
    user = get_current_user()
    projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
    total_members = User.query.filter_by(is_member=True).count()
    return render_template("dashboard.html", projects=projects, total_members=total_members, current_user=user)

@web_bp.route("/project/new", methods=["GET", "POST"])
@member_required
def create_project():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        raw_description = request.form.get("description", "").strip()
        project_type = request.form.get("project_type", "Workshop")
        target_wiki = request.form.get("target_wiki", "ar.wikipedia.org")
        status = request.form.get("status", "In Progress")
        co_orgs_raw = request.form.get("co_organizers", "")
        is_contest = bool(request.form.get("is_contest"))
        jury_raw = request.form.get("jury_members", "")

        # Sanitize HTML description against stored XSS
        safe_description = bleach.clean(
            raw_description,
            tags=["p", "b", "i", "strong", "em", "ul", "ol", "li", "a", "br"],
            attributes={"a": ["href", "title"]},
            strip=True
        )

        co_organizers = [u.strip() for u in co_orgs_raw.split(",") if u.strip()]
        jury_members = [j.strip() for j in jury_raw.split(",") if j.strip()] if is_contest else []

        new_project = Project(
            title=title,
            description=safe_description,
            project_type=project_type,
            target_wiki=target_wiki,
            status=status,
            lead_organizer=session.get("username"),
            co_organizers=co_organizers,
            is_contest=is_contest,
            jury_members=jury_members
        )
        db.session.add(new_project)
        db.session.commit()
        flash("Project activity created successfully!", "success")
        return redirect(url_for("web.dashboard"))

    return render_template("project_form.html", project=None)

@web_bp.route("/project/<int:project_id>/edit", methods=["GET", "POST"])
@project_editor_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == "POST":
        project.title = request.form.get("title", "").strip()
        raw_description = request.form.get("description", "").strip()
        project.description = bleach.clean(
            raw_description,
            tags=["p", "b", "i", "strong", "em", "ul", "ol", "li", "a", "br"],
            attributes={"a": ["href", "title"]},
            strip=True
        )
        project.project_type = request.form.get("project_type", project.project_type)
        project.target_wiki = request.form.get("target_wiki", project.target_wiki)
        project.status = request.form.get("status", project.status)
        project.is_contest = bool(request.form.get("is_contest"))
        
        co_orgs_raw = request.form.get("co_organizers", "")
        project.co_organizers = [u.strip() for u in co_orgs_raw.split(",") if u.strip()]
        
        jury_raw = request.form.get("jury_members", "")
        project.jury_members = [j.strip() for j in jury_raw.split(",") if j.strip()] if project.is_contest else []

        db.session.commit()
        flash("Project updated successfully!", "success")
        return redirect(url_for("web.dashboard"))

    return render_template("project_form.html", project=project)

@web_bp.route("/export")
def export_view():
    return render_template("export.html")