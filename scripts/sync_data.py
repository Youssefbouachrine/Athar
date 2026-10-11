#!/usr/bin/env python3
"""
Scheduled Background Worker for Toolforge
Runs every 4 hours to synchronize member roster and query CentralAuth global stats.
"""
import requests
from config import Config
from app import create_app, db
from app.models import User, StatSnapshot
from scripts.parse_members import fetch_members_from_meta

def fetch_global_stats(username):
    url = "https://meta.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "meta": "globaluserinfo",
        "guiuser": username,
        "guiprop": "editcount|merged",
        "format": "json"
    }
    headers = {"User-Agent": Config.USER_AGENT}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10).json()
        gui = resp.get("query", {}).get("globaluserinfo", {})
        
        breakdown = {}
        for item in gui.get("merged", []):
            if item.get("editcount", 0) > 0:
                breakdown[item.get("wiki")] = item.get("editcount")

        return {
            "total_edits": gui.get("editcount", 0),
            "home_wiki": gui.get("home", "ar.wikipedia.org"),
            "wiki_breakdown": breakdown
        }
    except Exception as e:
        print(f"[Warning] Could not fetch stats for {username}: {e}")
        return None

def run_sync():
    app = create_app()
    with app.app_context():
        print("[Sync] Fetching member list from Meta-Wiki...")
        usernames = fetch_members_from_meta()
        if not usernames:
            print("[Sync] Retaining existing database cache.")
            return

        for username in usernames:
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, is_member=True)
                db.session.add(user)
                db.session.flush()

            stats = fetch_global_stats(username)
            if stats:
                snapshot = StatSnapshot(
                    user_id=user.id,
                    total_edits=stats["total_edits"],
                    home_wiki=stats["home_wiki"],
                    wiki_breakdown=stats["wiki_breakdown"]
                )
                db.session.add(snapshot)

        db.session.commit()
        print(f"[Sync] Successfully synchronized {len(usernames)} members to database.")

if __name__ == "__main__":
    run_sync()
