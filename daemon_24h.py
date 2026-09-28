"""
daemon_24h.py
Autonomous Competitor Intelligence Monitor & Scheduled Briefing Daemon.
Scans competitor signals, tracks Google Sheet updates, and dispatches
professional 1-page executive reports via headless SMTP at:
- 9:00 PM PHT (21:00)
- 00:00 H PHT (Midnight)
Completely headless: NEVER opens macOS Mail.app.
"""
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from news_signals import fetch_competitor_news
from ads_tracker import get_public_ad_transparency_links
from summarizer import generate_competitor_summary, analyze_news_item_threat
from sheets_syncer import log_to_csv, sync_to_google_sheets_webhook
from db_manager import get_all_monitored_competitors
from scheduled_briefing_runner import run_scheduled_briefing

DEFAULT_COMPETITORS = [
    {"name": "RoofLife Canada", "domain": "rooflifecanada.com"},
    {"name": "Nasiol", "domain": "nasiol.com"},
    {"name": "Reviva Roof", "domain": "revivaroof.com"},
    {"name": "Spray-Net", "domain": "spray-net.com"},
    {"name": "ArmoveX", "domain": "armovex.com"},
    {"name": "Zinox Coating", "domain": "zinoxcoating.com"},
    {"name": "Roof Maxx", "domain": "roofmaxx.com"},
    {"name": "Sure Roof Pros", "domain": "sureroofpros.com"},
    {"name": "Ever Roof", "domain": "everroof.com"},
    {"name": "OnYa Roof", "domain": "onyaroof.com"}
]

def get_competitors_list():
    try:
        comps = get_all_monitored_competitors()
        return comps if comps else DEFAULT_COMPETITORS
    except Exception:
        return DEFAULT_COMPETITORS

def notify_macos(title: str, message: str):
    """Sends a native macOS desktop notification."""
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception:
        pass

def get_seconds_until_next_pht_slot(now=None) -> tuple:
    """Calculates wait time in seconds until the next 21:00 PHT or 00:00 H PHT."""
    if now is None:
        now = datetime.now()
    today_21 = now.replace(hour=21, minute=0, second=0, microsecond=0)
    today_00 = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_00 = today_00 + timedelta(days=1)
    tomorrow_21 = today_21 + timedelta(days=1)

    candidates = []
    if today_00 > now:
        candidates.append((today_00, "00:00 H PHT (Midnight)"))
    if today_21 > now:
        candidates.append((today_21, "9:00 PM PHT (21:00)"))
    if tomorrow_00 > now:
        candidates.append((tomorrow_00, "00:00 H PHT (Midnight tomorrow)"))
    if tomorrow_21 > now:
        candidates.append((tomorrow_21, "9:00 PM PHT (21:00 tomorrow)"))

    next_time, label = min(candidates, key=lambda x: x[0])
    wait_secs = int((next_time - now).total_seconds())
    return wait_secs, next_time.strftime("%Y-%m-%d %H:%M:%S PHT"), label

def start_scheduled_pht_loop():
    """Continuously runs and triggers scans and email briefings at 9 PM and 00:00 H PHT."""
    print("=" * 70)
    print("GONANO COMPETITOR INTELLIGENCE // PHT SCHEDULED DAEMON ACTIVE")
    print("Schedule: Every 9:00 PM PHT (21:00) and 00:00 H PHT (Midnight)")
    print("Mode: Headless background execution (Mail.app will NEVER open)")
    print("=" * 70)

    while True:
        wait_secs, next_slot_str, label = get_seconds_until_next_pht_slot()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S PHT')}] Next scheduled run: {next_slot_str} ({label})")
        print(f"Waiting for {wait_secs} seconds ({wait_secs/3600:.2f} hours)...")
        
        # Sleep until the exact scheduled minute
        time.sleep(max(1, wait_secs))

        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S PHT')}] Triggering scheduled bi-daily briefing...")
        try:
            res = run_scheduled_briefing()
            notify_macos("Competitor Intelligence Tool", f"Scheduled briefing sent for {label}")
        except Exception as e:
            print(f"Error during scheduled execution: {e}")

        # Sleep 60 seconds to avoid double-triggering in the same minute
        time.sleep(65)

if __name__ == "__main__":
    if "--now" in sys.argv or "--run-once" in sys.argv:
        run_scheduled_briefing()
    else:
        start_scheduled_pht_loop()
