"""
scheduled_briefing_runner.py
Automated Scheduled Runner for Bi-Daily Competitor Intelligence Briefings.
Triggered automatically at 9:00 PM PHT (21:00) and 00:00 H PHT (Midnight).
Performs:
1. Live competitive signal scan
2. Google Sheets tracker synchronization
3. Generates 1-page executive brief (Updates on News, New Competitors, Findings)
4. Headless email dispatch without opening macOS Mail.app
"""
import os
import sys
from datetime import datetime
from report_generator import build_executive_one_pager
from email_dispatcher import send_headless_email, get_smtp_config
from db_manager import get_all_monitored_competitors, save_signals_to_db
from news_signals import fetch_competitor_news
import sync_competitor_tracker

LOG_FILE = os.path.join(os.path.dirname(__file__), "scheduled_briefings.log")

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S PHT")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_scheduled_briefing():
    log("Starting automated scheduled intelligence scan...")

    # 1. Sync latest Google Sheets tracker data
    try:
        log("Synchronizing Google Sheets Competitor Tracker records...")
        sync_competitor_tracker.run_sync()
        log("Google Sheets sync completed successfully.")
    except Exception as e:
        log(f"Warning: Sheet sync encountered exception: {e}")

    # 2. Live quick news scan across top competitors
    try:
        log("Scanning latest news and press releases for key competitors...")
        comps = get_all_monitored_competitors()
        priority_comps = [c["name"] for c in comps[:6]] # RoofLife, Nasiol, RevivaRoof, Spray-Net, etc.
        for cname in priority_comps:
            news = fetch_competitor_news(cname, limit=2)
            if news:
                save_signals_to_db(news, cname)
        log(f"News scan completed across {len(priority_comps)} priority rivals.")
    except Exception as e:
        log(f"Warning: News scan encountered exception: {e}")

    # 3. Generate 1-page executive report (Zero emojis, strict professional structure)
    log("Compiling executive 1-page report...")
    report = build_executive_one_pager()
    plain_text = report["plain_text"]
    html_content = report["html"]
    timestamp = report["timestamp"]

    # 4. Dispatch headless email
    cfg = get_smtp_config()
    recipient = cfg["recipient"] or "gonzalesmiguelcarlo@gmail.com"
    subject = f"[COMPETITOR INTELLIGENCE] Executive Briefing ({timestamp})"

    log(f"Dispatching headless email to {recipient} without launching Mail.app...")
    result = send_headless_email(
        to_email=recipient,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content
    )

    if result["status"] == "success":
        log(f"SUCCESS: Intelligence briefing delivered to {recipient} via {result['method']}.")
    elif result["status"] == "config_needed":
        log(f"CONFIG NOTICE: {result['message']}. Local report saved to {result.get('local_path')}.")
    else:
        log(f"DELIVERY ISSUE: {result.get('message')}. Local report saved to {result.get('local_path')}.")

    log("Automated scheduled briefing run complete.")
    return result

if __name__ == "__main__":
    run_scheduled_briefing()
