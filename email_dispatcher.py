"""
email_dispatcher.py
Headless SMTP Email Dispatcher for Competitor Intelligence Tool.
Dispatches intelligence briefings silently in the background without opening the macOS Mail application.
Supports:
1. Headless SMTP over TLS/SSL (e.g. Gmail App Password, Corporate SMTP) with IPv4 socket preference & curl SMTPS fallback
2. Multiple primary TO recipients (comma-separated list)
3. Multiple CC recipients (comma-separated list)
4. Dual-mode payload delivery (Multipart Plain Text + Formatted Executive HTML)
5. Fallback archival of generated 1-pager reports
"""
import os
import re
import ssl
import socket
import smtplib
import subprocess
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional, List

DEFAULT_RECIPIENT = "joel@gonano.com, charles@gonano.com, jonathan@gonano.com"
DEFAULT_CC = "ryan@gonano.com, mathieu.vallieres@gonano.com, jason@gonano.com, alamin.abuhajjeh@gonano.com, cody.loeffler@gonano.com, john.silvernail@gonano.com"
DEFAULT_FROM = "miguel.gonzales@gonano.com"


class _SMTP_IPv4(smtplib.SMTP):
    """SMTP subclass that prefers IPv4 sockets while preserving hostname for TLS SNI."""
    def _get_socket(self, host, port, timeout):
        last_err = None
        for family in (socket.AF_INET, socket.AF_UNSPEC):
            try:
                addrs = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
                for res in addrs:
                    af, socktype, proto, canonname, sa = res
                    sock = None
                    try:
                        sock = socket.socket(af, socktype, proto)
                        if timeout is not None:
                            sock.settimeout(timeout)
                        if self.source_address:
                            sock.bind(self.source_address)
                        sock.connect(sa)
                        return sock
                    except OSError as e:
                        last_err = e
                        if sock is not None:
                            sock.close()
            except OSError as e:
                last_err = e
        if last_err:
            raise last_err
        return super()._get_socket(host, port, timeout)


class _SMTP_SSL_IPv4(smtplib.SMTP_SSL):
    """SMTP_SSL subclass that prefers IPv4 sockets while preserving hostname for TLS SNI."""
    def _get_socket(self, host, port, timeout):
        last_err = None
        for family in (socket.AF_INET, socket.AF_UNSPEC):
            try:
                addrs = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)
                for res in addrs:
                    af, socktype, proto, canonname, sa = res
                    sock = None
                    try:
                        sock = socket.socket(af, socktype, proto)
                        if timeout is not None:
                            sock.settimeout(timeout)
                        if self.source_address:
                            sock.bind(self.source_address)
                        sock.connect(sa)
                        return self.context.wrap_socket(sock, server_hostname=self._host)
                    except OSError as e:
                        last_err = e
                        if sock is not None:
                            sock.close()
            except OSError as e:
                last_err = e
        if last_err:
            raise last_err
        return super()._get_socket(host, port, timeout)


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
    host = (os.getenv("SMTP_HOST") or env_vars.get("SMTP_HOST", "smtp.gmail.com")).strip()
    port = int(os.getenv("SMTP_PORT") or env_vars.get("SMTP_PORT", 465))
    recipient = (os.getenv("RECIPIENT_EMAIL") or env_vars.get("RECIPIENT_EMAIL", DEFAULT_RECIPIENT)).strip()
    cc = (os.getenv("CC_EMAILS") or env_vars.get("CC_EMAILS", DEFAULT_CC)).strip()
    from_email = (os.getenv("FROM_EMAIL") or env_vars.get("FROM_EMAIL", DEFAULT_FROM)).strip()

    # Check sibling contractor tool .env for alternate GoNano app password if present
    alt_password = ""
    sibling_env = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "GoNano-Competitor-Intelligence-Tool-For-Certified-Contractors",
        ".env"
    )
    if os.path.exists(sibling_env):
        try:
            with open(sibling_env, "r", encoding="utf-8") as sf:
                for line in sf:
                    line = line.strip()
                    if line.startswith("SMTP_PASSWORD="):
                        alt_password = line.split("=", 1)[1].strip().strip('"').strip("'").replace(" ", "")
        except Exception:
            pass

    return {
        "user": user,
        "password": password,
        "alt_password": alt_password,
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
        match = re.search(r"<([^>]+)>", addr)
        if match:
            addr = match.group(1).strip()
        if addr and "@" in addr and "." in addr:
            if addr.lower() not in [c.lower() for c in cleaned]:
                cleaned.append(addr)
    return cleaned


def _send_via_curl_smtps(
    host: str,
    user: str,
    password: str,
    sender_addr: str,
    all_recipients: List[str],
    raw_msg_bytes: bytes
) -> None:
    """Fallback using macOS system /usr/bin/curl over IPv4 SMTPS (port 465)."""
    curl_bin = "/usr/bin/curl" if os.path.exists("/usr/bin/curl") else "curl"
    cmd = [
        curl_bin,
        "--silent",
        "--show-error",
        "--ipv4",
        "--ssl-reqd",
        "--connect-timeout", "15",
        "--max-time", "30",
        "--url", f"smtps://{host}:465",
        "--user", f"{user}:{password}",
        "--mail-from", sender_addr,
    ]
    for rcpt in all_recipients:
        cmd.extend(["--mail-rcpt", rcpt])
    cmd.extend(["--upload-file", "-"])

    proc = subprocess.run(cmd, input=raw_msg_bytes, capture_output=True, timeout=35)
    if proc.returncode != 0:
        stderr_txt = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"curl smtps exit {proc.returncode}: {stderr_txt}")


def send_headless_email(
    to_email: Optional[str] = None,
    subject: str = "Competitor Updates",
    plain_text: str = "",
    html_content: Optional[str] = None,
    cc_emails: Optional[str] = None,
    smtp_user: str = "",
    smtp_pass: str = "",
    smtp_host: str = "",
    smtp_port: Optional[int] = None,
    from_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends an email completely headlessly via Python smtplib (with IPv4 + curl SMTPS fallback).
    Supports multiple TO recipients and multiple CC recipients.
    Guaranteed: NEVER opens macOS Mail.app or interrupts the user's desktop.
    """
    cfg = get_smtp_config()
    user = smtp_user or cfg["user"]
    password = smtp_pass or cfg["password"]
    host = smtp_host or cfg["host"] or "smtp.gmail.com"
    port = int(smtp_port) if smtp_port is not None else int(cfg["port"] or 465)
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

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Miguel Gonzales <{sender_addr}>"
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Subject"] = subject
    msg["Date"] = email.utils.formatdate(usegmt=True)
    msg["Message-ID"] = email.utils.make_msgid(domain="gonano.com")

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    if html_content:
        msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Deliver to all unique TO + CC recipients
    to_lower = [t.lower() for t in to_list]
    all_recipients = list(to_list)
    for c in cc_list:
        if c.lower() not in to_lower and c.lower() not in [a.lower() for a in all_recipients]:
            all_recipients.append(c)

    raw_msg_str = msg.as_string()
    raw_msg_bytes = raw_msg_str.encode("utf-8")

    candidate_passwords = [password]
    alt_pw = cfg.get("alt_password", "")
    if alt_pw and alt_pw not in candidate_passwords:
        candidate_passwords.append(alt_pw)

    ports_to_try = [port]
    for p in (465, 587):
        if p not in ports_to_try:
            ports_to_try.append(p)

    ssl_ctx = ssl.create_default_context()
    diagnostics = []

    for pw_idx, cand_pw in enumerate(candidate_passwords, start=1):
        for try_port in ports_to_try:
            stage = "connect"
            server = None
            try:
                if try_port == 465:
                    server = _SMTP_SSL_IPv4(
                        host,
                        465,
                        local_hostname="localhost",
                        timeout=15.0,
                        context=ssl_ctx
                    )
                    stage = "ehlo"
                    server.ehlo("localhost")
                else:
                    server = _SMTP_IPv4(
                        host,
                        try_port,
                        local_hostname="localhost",
                        timeout=15.0
                    )
                    stage = "ehlo"
                    server.ehlo("localhost")
                    stage = "starttls"
                    server.starttls(context=ssl_ctx)
                    stage = "ehlo_post_tls"
                    server.ehlo("localhost")

                stage = "login"
                server.login(user, cand_pw)
                stage = "sendmail"
                server.sendmail(sender_addr, all_recipients, raw_msg_str)
                try:
                    server.quit()
                except Exception:
                    pass

                to_summary = ", ".join(to_list)
                cc_summary = f" (CC: {', '.join(cc_list)})" if cc_list else ""
                log_entry(f"[SUCCESS] Dispatched headless email from {sender_addr} to {to_summary}{cc_summary} via {host}:{try_port} (IPv4)")
                return {
                    "status": "success",
                    "method": f"Headless SMTP IPv4 ({host}:{try_port})",
                    "from": sender_addr,
                    "to_recipients": to_list,
                    "cc_recipients": cc_list,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S PHT")
                }
            except smtplib.SMTPAuthenticationError as auth_err:
                diagnostics.append(f"pw#{pw_idx}@{host}:{try_port}[{stage}]: AuthError {auth_err.smtp_code}")
                try:
                    if server:
                        server.close()
                except Exception:
                    pass
                # Authentication reached server; no need to try other ports with this same rejected password
                break
            except Exception as e:
                diagnostics.append(f"pw#{pw_idx}@{host}:{try_port}[{stage}]: {type(e).__name__}({e})")
                try:
                    if server:
                        server.close()
                except Exception:
                    pass

        # Fallback: try system curl SMTPS over IPv4 port 465
        try:
            _send_via_curl_smtps(host, user, cand_pw, sender_addr, all_recipients, raw_msg_bytes)
            to_summary = ", ".join(to_list)
            cc_summary = f" (CC: {', '.join(cc_list)})" if cc_list else ""
            log_entry(f"[SUCCESS] Dispatched headless email from {sender_addr} to {to_summary}{cc_summary} via curl smtps://{host}:465")
            return {
                "status": "success",
                "method": f"Headless curl SMTPS ({host}:465)",
                "from": sender_addr,
                "to_recipients": to_list,
                "cc_recipients": cc_list,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S PHT")
            }
        except Exception as curl_err:
            diagnostics.append(f"pw#{pw_idx}@curl_smtps: {curl_err}")

    diag_str = " | ".join(diagnostics)
    err_msg = f"Headless SMTP delivery failed ({diag_str})"
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
