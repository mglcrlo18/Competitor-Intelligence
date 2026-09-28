"""
email_dispatcher.py
Headless SMTP Email Dispatcher for Competitor Intelligence Tool.
Dispatches intelligence briefings silently in the background without opening the macOS Mail application.
Supports:
1. Headless SMTP over TLS/SSL (e.g. Gmail App Password, Corporate SMTP)
2. Multiple primary TO recipients (comma-separated list)
3. Multiple CC recipients (comma-separated list)
4. Dual-mode payload delivery (Multipart Plain Text + Formatted Executive HTML)
5. Fallback archival of generated 1-pager reports
"""
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional, List

DEFAULT_RECIPIENT = "joel@gonano.com, charles@gonano.com, jonathan@gonano.com"
DEFAULT_CC = "ryan@gonano.com, mathieu.vallieres@gonano.com, jason@gonano.com, alamin.abuhajjeh@gonano.com, cody.loeffler@gonano.com, john.silvernail@gonano.com"
DEFAULT_FROM = "miguel.gonzales@gonano.com"

def get_smtp_config() -> Dict[str, Any]:
    """Retrieves SMTP configuration from environment variables or .env file."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")

    user = (os.getenv("SMTP_USER") or env_vars.get("SMTP_USER", DEFAULT_FROM)).strip()
    password = (os.getenv("SMTP_PASSWORD") or env_vars.get("SMTP_PASSWORD", "")).replace(" ", "").strip()
    host = os.getenv("SMTP_HOST") or env_vars.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT") or env_vars.get("SMTP_PORT", 587))
    recipient = (os.getenv("RECIPIENT_EMAIL") or env_vars.get("RECIPIENT_EMAIL", DEFAULT_RECIPIENT)).strip()
    cc = (os.getenv("CC_EMAILS") or env_vars.get("CC_EMAILS", DEFAULT_CC)).strip()
    from_email = (os.getenv("FROM_EMAIL") or env_vars.get("FROM_EMAIL", DEFAULT_FROM)).strip()

    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "recipient": recipient,
        "cc": cc,
        "from_email": from_email
    }

def parse_email_list(raw_input: Optional[str]) -> List[str]:
    """Parses a comma, semicolon, or newline-separated string of email addresses."""
    if not raw_input:
        return []
    items = re.split(r"[,;\n]", str(raw_input))
    cleaned = []
    for it in items:
        addr = it.strip()
        # Handle format like "Name <email@domain.com>"
        match = re.search(r"<([^>]+)>", addr)
        if match:
            addr = match.group(1).strip()
        if addr and "@" in addr and "." in addr:
            if addr.lower() not in [c.lower() for c in cleaned]:
                cleaned.append(addr)
    return cleaned

def send_headless_email(
    to_email: Optional[str] = None,
    subject: str = "Competitor Updates",
    plain_text: str = "",
    html_content: Optional[str] = None,
    cc_emails: Optional[str] = None,
    smtp_user: str = "",
    smtp_pass: str = "",
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    from_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends an email completely headlessly via Python smtplib.
    Supports multiple TO recipients and multiple CC recipients.
    Guaranteed: NEVER opens macOS Mail.app or interrupts the user's desktop.
    """
    cfg = get_smtp_config()
    user = smtp_user or cfg["user"]
    password = smtp_pass or cfg["password"]
    host = smtp_host or cfg["host"]
    port = smtp_port or cfg["port"]
    sender_addr = from_email or cfg.get("from_email") or user or DEFAULT_FROM

    # Parse primary TO recipients
    dest_raw = to_email if to_email is not None else cfg.get("recipient", DEFAULT_RECIPIENT)
    to_list = parse_email_list(dest_raw)
    if not to_list:
        to_list = parse_email_list(DEFAULT_RECIPIENT)

    # Parse CC recipients
    cc_raw = cc_emails if cc_emails is not None else cfg.get("cc", DEFAULT_CC)
    cc_list = parse_email_list(cc_raw)

    # Save local copy of report regardless
    report_txt_path = os.path.join(os.path.dirname(__file__), "latest_scheduled_report.txt")
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write(plain_text)

    if html_content:
        report_html_path = os.path.join(os.path.dirname(__file__), "latest_scheduled_report.html")
        with open(report_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    if not user or not password:
        msg = "SMTP credentials missing. Please set SMTP_USER and SMTP_PASSWORD in .env (or in Alerts tab) to enable headless dispatch."
        log_entry(f"[CONFIG_NEEDED] {msg} -> Saved local report to {report_txt_path}")
        return {
            "status": "config_needed",
            "message": msg,
            "local_path": report_txt_path,
            "to_recipients": to_list,
            "cc_recipients": cc_list
        }

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Miguel Gonzales <{sender_addr}>"
        msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")

        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        if html_content:
            msg.attach(MIMEText(html_content, "html", "utf-8"))

        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15.0)
        else:
            server = smtplib.SMTP(host, port, timeout=15.0)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(user, password)
        
        # Deliver to all unique TO + CC recipients
        to_lower = [t.lower() for t in to_list]
        all_recipients = list(to_list)
        for c in cc_list:
            if c.lower() not in to_lower and c.lower() not in [a.lower() for a in all_recipients]:
                all_recipients.append(c)

        server.sendmail(sender_addr, all_recipients, msg.as_string())
        server.quit()

        to_summary = ", ".join(to_list)
        cc_summary = f" (CC: {', '.join(cc_list)})" if cc_list else ""
        log_entry(f"[SUCCESS] Dispatched headless email from {sender_addr} to {to_summary}{cc_summary} via {host}:{port}")
        return {
            "status": "success",
            "method": f"Headless SMTP ({host}:{port})",
            "from": sender_addr,
            "to_recipients": to_list,
            "cc_recipients": cc_list,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S PHT")
        }
    except Exception as e:
        err_msg = f"Headless SMTP delivery failed: {str(e)}"
        log_entry(f"[ERROR] {err_msg}")
        return {
            "status": "error",
            "message": err_msg,
            "local_path": report_txt_path,
            "to_recipients": to_list,
            "cc_recipients": cc_list
        }

def log_entry(text: str):
    """Appends audit record to email_dispatches.log."""
    log_path = os.path.join(os.path.dirname(__file__), "email_dispatches.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S PHT")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")
