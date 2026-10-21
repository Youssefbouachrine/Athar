import csv
import io
from flask import Blueprint, jsonify, request, Response, session
from app.models import Community, Project, User, StatSnapshot, CommunityMember
from app.oauth import member_required
from app import db
from sqlalchemy import func
import bleach

api_bp = Blueprint("api", __name__)

@api_bp.route("/communities", methods=["GET"])
def get_communities():
    communities = Community.query.all()
    if communities:
        return jsonify([community.to_dict() for community in communities])
    else:
        return jsonify({"error": "no community found"})
        

@api_bp.route("/stats")
def get_stats():
    total_members = User.query.filter_by(is_member=True).count()
    total_projects = Project.query.count()
    
    latest_snapshots = StatSnapshot.query.order_by(StatSnapshot.recorded_at.desc()).limit(100).all()
    total_edits = sum(s.total_edits for s in latest_snapshots)

    return jsonify({
        "total_members": total_members,
        "total_projects": total_projects,
        "total_edits": total_edits
    })
    
@api_bp.route("/<string:slug>/stats", methods=["GET"])
def slug_Stat(slug):
    community = Community.query.filter_by(slug=slug).first()
    if not community:
        return jsonify({"error": "Community not found"}), 404
        
    count_community_member = db.session.query(func.count(CommunityMember.user_id)).filter(CommunityMember.community_id == community.id).scalar()
    count_project = db.session.query(func.count(Project.id)).filter(Project.community_id == community.id).scalar()
    
    return jsonify({
        "total_community_member": count_community_member,
        "total_project_member": count_project
    })

    
@api_bp.route("/<string:slug>/members", methods=["GET"])
def list_members(slug):
    community = Community.query.filter_by(slug=slug).first()
    if not community:
        return jsonify({"error": "Community not found"}), 404
        
    community_members = CommunityMember.query.filter_by(community_id=community.id).all()
    if not community_members:
        return jsonify({"error": "No member in this community"})
        
    members = []
    for cm in community_members:
        member = User.query.get(cm.user_id)
        if not member:
            continue
        last_snapshot = StatSnapshot.query.filter_by(user_id=member.id).order_by(StatSnapshot.recorded_at.desc()).first()
        members.append({
            "id": member.id,
            "username": member.username,
            "is_member": member.is_member,
            "first_seen": member.first_seen.isoformat() if member.first_seen else None,
            "last_synced": member.last_synced.isoformat() if member.last_synced else None,
            "total_edits": last_snapshot.total_edits if last_snapshot else 0
        })
    return jsonify(members), 200
    
@api_bp.route("/<string:slug>/projects", methods=["GET"])
def list_slug_project(slug):
    community = Community.query.filter_by(slug=slug).first()
    if not community:
        return jsonify({"error": "Community not found"}), 404
    projects = Project.query.filter_by(community_id=community.id).all()
    if not projects:
        return jsonify([]), 200
    return jsonify([p.to_dict() for p in projects]), 200
    
    
@api_bp.route("/<string:slug>/project", methods=["POST"])
@member_required
def create_projetct(slug):
    community = Community.query.filter_by(slug=slug).first()
    if not community:
        return jsonify({"error": "Community not found"}), 404
        
    community_id = community.id
    title = request.form.get("title", "").strip()
    raw_description = request.form.get("description", "").strip()
    project_type = request.form.get("project_type", "Workshop")
    target_wiki = request.form.get("target_wiki", "ar.wikipedia.org")
    status = request.form.get("status", "In Progress")
    co_orgs_raw = request.form.get("co_organizers", "")
    is_contest = bool(request.form.get("is_contest"))
    jury_raw = request.form.get("jury_members", "")
    
    safe_description = bleach.clean(
        raw_description,
        tags=["p", "b", "i", "strong", "em", "ul", "ol", "li", "a", "br"],
        attributes={"a": ["href", "title"]},
        strip=True
    )

    co_organizers = [u.strip() for u in co_orgs_raw.split(",") if u.strip()]
    jury_members = [j.strip() for j in jury_raw.split(",") if j.strip()] if is_contest else []
        
    new_project = Project(
        community_id=community_id,
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
    
    return jsonify({"message": "Project created successfully"}), 201


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
            p.created_at.strftime("%Y-%m-%d") if p.created_at else ""
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=athar_projects.csv"}
    )

    
@api_bp.route("/<string:slug>/export", methods=["GET"])
def exp_community_projects(slug):
    community = Community.query.filter_by(slug=slug).first()
    if not community:
        return jsonify({"error": "Community not found"}), 404
        
    projects = Project.query.filter_by(community_id=community.id).order_by(Project.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)

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
            p.created_at.strftime("%Y-%m-%d") if p.created_at else ""
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=athar_projects.csv"}
    )