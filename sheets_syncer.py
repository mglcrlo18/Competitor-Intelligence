"""
sheets_syncer.py
Handles syncing 24/7 competitor intelligence findings to Google Sheets and local CSV archive.
Synced with the master Google Sheet:
https://docs.google.com/spreadsheets/d/1FfQwtbauwbzFXLqmNmaaktAge4ts9wXihqVaeT0JGB0/edit?usp=sharing
"""
import os
import csv
from datetime import datetime
from typing import Dict, Any, List
import httpx

CSV_PATH = os.path.join(os.path.dirname(__file__), "competitor_findings.csv")
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1FfQwtbauwbzFXLqmNmaaktAge4ts9wXihqVaeT0JGB0/edit?usp=sharing"
SPREADSHEET_ID = "1FfQwtbauwbzFXLqmNmaaktAge4ts9wXihqVaeT0JGB0"

FIELDNAMES = [
    "timestamp", "competitor", "category",
    "title", "threat_level", "gemini_verdict", "recommended_action", "url"
]

def log_to_csv(rows: List[Dict[str, Any]]):
    """
    Appends 24/7 competitor findings to the local CSV archive.
    """
    file_exists = os.path.exists(CSV_PATH)
    
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({
                "timestamp": row.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M")),
                "competitor": row.get("competitor", ""),
                "category": row.get("category", "General News"),
                "title": row.get("title", ""),
                "threat_level": row.get("threat_level", "Moderate"),
                "gemini_verdict": row.get("gemini_verdict", row.get("summary", "")),
                "recommended_action": row.get("recommended_action", "Monitor and benchmark against GoNano technology."),
                "url": row.get("url", "")
            })

def read_recent_findings(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Reads the most recent logged findings from the CSV archive.
    """
    if not os.path.exists(CSV_PATH):
        return []
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows[-limit:][::-1]

def sync_to_google_sheets_webhook(webhook_url: str, rows: List[Dict[str, Any]]) -> bool:
    """
    Sends rows to Google Sheet via Google Apps Script Webhook.
    """
    if not webhook_url:
        return False
    try:
        res = httpx.post(webhook_url, json={"rows": rows}, timeout=15.0)
        return res.status_code == 200
    except Exception as e:
        print(f"Failed to post to Google Sheets webhook: {e}")
        return False

def get_all_competitors_list() -> List[str]:
    """
    Returns the comprehensive, deduplicated list of competitors loaded from db_manager
    and the Google Sheet tracker.
    """
    try:
        import db_manager
        names = db_manager.get_all_competitor_names()
        if names:
            return names
    except Exception:
        pass
    
    sheet_csv = os.path.join(os.path.dirname(__file__), "competitor_sheet.csv")
    if os.path.exists(sheet_csv):
        comps = set()
        with open(sheet_csv, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                c = r.get("Competitor", "").strip()
                if c:
                    comps.add(c)
        comps.add("GoNano (Your Brand)")
        return sorted(list(comps), key=lambda x: (x != "GoNano (Your Brand)", x.lower()))
        
    return ["GoNano (Your Brand)", "RoofLife Canada", "Nasiol (Artekya)", "RevivaRoof", "Spray-Net", "ArmoveX", "Zinox Coating"]

