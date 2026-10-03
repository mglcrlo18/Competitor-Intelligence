"""
scheduled_briefing_runner.py
Automated Scheduled Runner for GoNano Competitor Intelligence Briefings.
Triggered automatically at 00:00 H PHT (Midnight).
Includes:
- Distributed Idempotency Guard (dispatch_lock.json) preventing duplicate dispatches
- Live competitive signal scan
- Google Sheets tracker synchronization
- 1-Page executive brief generation (Updates on News, Strategic Findings)
- Headless email dispatch from miguel.gonzales@gonano.com to fixed distribution
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from report_generator import build_executive_one_pager
from email_dispatcher import send_headless_email, get_smtp_config
from db_manager import get_all_monitored_competitors, save_signals_to_db
from news_signals import fetch_competitor_news
from youtube_tracker import search_youtube_videos
from osint_listener import fetch_reddit_mentions
import sync_competitor_tracker

LOG_FILE = os.path.join(os.path.dirname(__file__), "scheduled_briefings.log")
LOCK_FILE = os.path.join(os.path.dirname(__file__), "dispatch_lock.json")

def get_current_est_pht_times():
    now_utc = datetime.now(timezone.utc)
    now_est = now_utc.astimezone(ZoneInfo("America/New_York"))
    now_pht = now_utc.astimezone(ZoneInfo("Asia/Manila"))
    return now_est, now_pht

def log(msg: str):
    now_est, now_pht = get_current_est_pht_times()
    ts = f"{now_est.strftime('%Y-%m-%d %H:%M:%S %Z')} | {now_pht.strftime('%Y-%m-%d %H:%M:%S')} PHT"
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def get_current_pht_time():
    """Returns current datetime in Philippine Time (UTC+8)."""
    return datetime.now(ZoneInfo("Asia/Manila"))

def is_already_dispatched_today(force: bool = False) -> bool:
    """
    Evaluates whether an intelligence briefing has already been dispatched today.
    Checks dispatch_lock.json and rejects duplicate execution.
    """
    if force:
        return False

    # In local environment, attempt a quick git pull to see if cloud already ran
    if not os.getenv("GITHUB_ACTIONS"):
        try:
            repo_dir = os.path.dirname(__file__)
            subprocess.run(
                ["git", "-C", repo_dir, "pull", "--quiet", "--rebase"],
                timeout=8,
                capture_output=True
            )
        except Exception:
            pass

    if not os.path.exists(LOCK_FILE):
        return False

    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        today_pht = get_current_pht_time().strftime("%Y-%m-%d")
        last_date = data.get("date_pht", "")
        last_status = data.get("status", "")

        if last_date == today_pht and last_status == "SENT":
            src = data.get("source", "another environment")
            dispatched_time = data.get("dispatched_at", "earlier today")
            log(f"[DEDUPLICATION GUARD] Briefing already dispatched for today ({today_pht}) at {dispatched_time} via {src}. Aborting run to prevent duplicate email delivery.")
            return True
    except Exception as e:
        log(f"Warning: Lockfile check encountered exception ({e}); proceeding cautiously.")

    return False

def record_dispatch_lock(source: str):
    """Records the dispatch lock and synchronizes it with the Git repository."""
    pht_now = get_current_pht_time()
    lock_data = {
        "date_pht": pht_now.strftime("%Y-%m-%d"),
        "dispatched_at": pht_now.strftime("%Y-%m-%d %H:%M:%S PHT"),
        "source": source,
        "status": "SENT"
    }
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)
    log(f"[LOCK RECORDED] Dispatch lock written for {lock_data['date_pht']} by {source}.")

    # If running locally with git access, commit & push lockfile to sync cloud
    if not os.getenv("GITHUB_ACTIONS"):
        try:
            repo_dir = os.path.dirname(__file__)
            subprocess.run(["git", "-C", repo_dir, "add", "dispatch_lock.json"], timeout=8, capture_output=True)
            subprocess.run(
                ["git", "-C", repo_dir, "commit", "-m", f"chore: update dispatch lock for {lock_data['date_pht']} [skip ci]"],
                timeout=8,
                capture_output=True
            )
            subprocess.run(["git", "-C", repo_dir, "push", "--quiet"], timeout=15, capture_output=True)
            log("[LOCK SYNCED] Dispatch lock successfully pushed to remote GitHub repository.")
        except Exception as e:
            log(f"Notice: Local lockfile written, remote git sync skipped ({e}).")

def run_scheduled_briefing(force: bool = False):
    # 0. Distributed Deduplication Pre-Flight Check
    if is_already_dispatched_today(force=force):
        return {
            "status": "skipped",
            "message": "Briefing already dispatched today. Deduplication guard prevented duplicate email."
        }

    log("Starting automated scheduled intelligence scan (00:00 H PHT)...")

    # 1. Sync latest Google Sheets tracker data
    try:
        log("Synchronizing Google Sheets Competitor Tracker records...")
        sync_competitor_tracker.run_sync()
        log("Google Sheets sync completed successfully.")
    except Exception as e:
        log(f"Warning: Sheet sync encountered exception: {e}")

    # 2. Live multi-source scan across ALL competitors (News + YouTube + Forums)
    try:
        comps = get_all_monitored_competitors()
        all_comp_names = []
        seen = set()
        for c in comps:
            cname = (c.get("name") or "").strip()
            if cname and cname.lower() not in seen:
                seen.add(cname.lower())
                all_comp_names.append(cname)

        log(f"Expanded Scraper Coverage: Scanning latest news, videos, and forum signals across all {len(all_comp_names)} competitors...")
        for cname in all_comp_names:
            # 2a. Verified News RSS
            try:
                news = fetch_competitor_news(cname, limit=2)
                if news:
                    save_signals_to_db(news, cname)
            except Exception:
                pass

            # 2b. YouTube Video Intelligence (low-quota search, order='date')
            try:
                vids = search_youtube_videos(f"{cname} roof", limit=1)
                if vids:
                    save_signals_to_db(vids, cname)
            except Exception:
                pass

            # 2c. Community Forum & Reddit Signals
            try:
                reddit_posts = fetch_reddit_mentions(cname, limit=1)
                if reddit_posts:
                    save_signals_to_db(reddit_posts, cname)
            except Exception:
                pass
        log(f"Multi-source intelligence scan completed across all {len(all_comp_names)} competitors.")
    except Exception as e:
        log(f"Warning: Intelligence scan encountered exception: {e}")

    # 3. Retrieve SMTP, recipient, and CC config
    cfg = get_smtp_config()
    recipient = cfg.get("recipient") or "joel@gonano.com, charles@gonano.com, jonathan@gonano.com"
    cc_emails = cfg.get("cc") or "ryan@gonano.com, mathieu.vallieres@gonano.com, jason@gonano.com, alamin.abuhajjeh@gonano.com, cody.loeffler@gonano.com, john.silvernail@gonano.com"
    from_addr = cfg.get("from_email") or "miguel.gonzales@gonano.com"

    # 4. Generate 1-page executive report
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

    if result.get("status") == "success":
        runner_source = "github_actions" if os.getenv("GITHUB_ACTIONS") else "local_macbook"
        record_dispatch_lock(source=runner_source)
        to_str = ", ".join(result.get("to_recipients", [recipient]))
        cc_str = ", ".join(result.get("cc_recipients", []))
        log(f"SUCCESS: Intelligence briefing delivered from {result.get('from', from_addr)} to [{to_str}] (CC: [{cc_str}]) via {result['method']}.")
    elif result.get("status") == "config_needed":
        log(f"CONFIG NOTICE: {result.get('message')}. Local report saved to {result.get('local_path')}.")
    else:
        log(f"DELIVERY ISSUE: {result.get('message')}. Local report saved to {result.get('local_path')}.")

    log("Automated scheduled briefing run complete.")
    return result

if __name__ == "__main__":
    force_run = "--force" in sys.argv
    run_scheduled_briefing(force=force_run)
