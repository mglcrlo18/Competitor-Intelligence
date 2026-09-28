"""
scheduled_briefing_runner.py
Automated Scheduled Runner for GoNano Competitor Intelligence Briefings.
Triggered automatically at 00:00 H PHT (Midnight).
Performs:
1. Live competitive signal scan
2. Google Sheets tracker synchronization
3. Generates 1-page executive brief (Updates on News, Strategic Findings)
4. Headless email dispatch from miguel.gonzales@gonano.com to:
   - TO: joel@gonano.com, charles@gonano.com, jonathan@gonano.com
   - CC: ryan@gonano.com, mathieu.vallieres@gonano.com, jason@gonano.com,
         alamin.abuhajjeh@gonano.com, cody.loeffler@gonano.com, john.silvernail@gonano.com
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
    log("Starting automated scheduled intelligence scan (00:00 H PHT)...")

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

    # 3. Retrieve SMTP, recipient, and CC config
    cfg = get_smtp_config()
    recipient = cfg.get("recipient") or "joel@gonano.com, charles@gonano.com, jonathan@gonano.com"
    cc_emails = cfg.get("cc") or "ryan@gonano.com, mathieu.vallieres@gonano.com, jason@gonano.com, alamin.abuhajjeh@gonano.com, cody.loeffler@gonano.com, john.silvernail@gonano.com"
    from_addr = cfg.get("from_email") or "miguel.gonzales@gonano.com"

    # 4. Generate 1-page executive report (Zero emojis, strict professional structure)
    log("Compiling executive 1-page report...")
    report = build_executive_one_pager(cc_recipients=cc_emails)
    plain_text = report["plain_text"]
    html_content = report["html"]
    timestamp = report["timestamp"]

    # 5. Subject: Competitor Updates as of [Date and Time]
    subject = f"Competitor Updates as of {timestamp}"

    log(f"Dispatching headless email from {from_addr} to {recipient} (CC: {cc_emails})...")
    result = send_headless_email(
        to_email=recipient,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content,
        cc_emails=cc_emails,
        from_email=from_addr
    )

    if result["status"] == "success":
        to_str = ", ".join(result.get("to_recipients", [recipient]))
        cc_str = ", ".join(result.get("cc_recipients", []))
        log(f"SUCCESS: Intelligence briefing delivered from {result.get('from', from_addr)} to [{to_str}] (CC: [{cc_str}]) via {result['method']}.")
    elif result["status"] == "config_needed":
        log(f"CONFIG NOTICE: {result['message']}. Local report saved to {result.get('local_path')}.")
    else:
        log(f"DELIVERY ISSUE: {result.get('message')}. Local report saved to {result.get('local_path')}.")

    log("Automated scheduled briefing run complete.")
    return result

if __name__ == "__main__":
    run_scheduled_briefing()
