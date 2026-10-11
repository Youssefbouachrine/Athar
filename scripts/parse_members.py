#!/usr/bin/env python3
"""
Member List Parser for Meta-Wiki
Extracts usernames using mwparserfromhell AST instead of fragile regex.
"""
import requests
import mwparserfromhell
from config import Config

def fetch_members_from_meta(page_title=None):
    if not page_title:
        page_title = Config.META_ROSTER_PAGE

    url = "https://meta.wikimedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext",
        "format": "json"
    }
    headers = {"User-Agent": Config.USER_AGENT}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        raw_wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
    except Exception as e:
        print(f"[Error] Failed to fetch Meta page: {e}")
        return []

    wikicode = mwparserfromhell.parse(raw_wikitext)
    members = []

    # Extract all wikilinks formatted like [[User:Username|...]]
    for link in wikicode.filter_wikilinks():
        target = str(link.title).strip()
        if target.startswith("User:"):
            clean_user = target.replace("User:", "").split("/")[0].strip()
            if clean_user and clean_user not in members:
                members.append(clean_user)

    return members

if __name__ == "__main__":
    roster = fetch_members_from_meta()
    print(f"Extracted {len(roster)} members: {roster[:5]}...")
