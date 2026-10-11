import csv
import io
from flask import Blueprint, jsonify, request, Response, session
from app.models import Project, User, StatSnapshot
from app.oauth import member_required, get_current_user
from app import db
import bleach

api_bp = Blueprint("api", __name__)

@api_bp.route("/stats")
def get_stats():
    total_members = User.query.filter_by(is_member=True).count()
    total_projects = Project.query.count()
    
    # Calculate aggregate edits across snapshots
    latest_snapshots = StatSnapshot.query.order_by(StatSnapshot.recorded_at.desc()).limit(100).all()
    total_edits = sum(s.total_edits for s in latest_snapshots)

    return jsonify({
        "total_members": total_members,
        "total_projects": total_projects,
        "total_edits": total_edits
    })

@api_bp.route("/projects", methods=["GET"])
def list_projects():
    status = request.args.get("status")
    project_type = request.args.get("type")
    
    query = Project.query
    if status:
        query = query.filter_by(status=status)
    if project_type:
        query = query.filter_by(project_type=project_type)
        
    projects = query.order_by(Project.created_at.desc()).all()
    return jsonify([p.to_dict() for p in projects])

@api_bp.route("/export")
def export_csv():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row formatted for Wikimedia reporting
    writer.writerow(["ID", "Title", "Type", "Target Wiki", "Status", "Lead Organizer", "Co-Organizers", "Is Contest", "Created At"])
    for p in projects:
        writer.writerow([
            p.id,
            p.title,
            p.project_type,
            p.target_wiki,
            p.status,
            p.lead_organizer,
            ", ".join(p.co_organizers or []),
            p.is_contest,
            p.created_at.strftime("%Y-%m-%d")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=athar_projects.csv"}
    )
