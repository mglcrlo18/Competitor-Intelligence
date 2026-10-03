"""
alerting_engine.py
C-Suite Automated Alerting & Webhook Dispatch Engine.
Dispatches critical market threat alerts to Telegram, Slack, Discord, and Email
whenever Key Competitive Indicators (KCIs) breach predefined thresholds.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import httpx

def format_alert_payload(competitor_name: str, kci_name: str, trigger_reason: str, severity: str = "CRITICAL") -> Dict[str, Any]:
    """Formats standardized C-suite alert payload."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "timestamp": timestamp,
        "title": f"[ALERT] [CRO ALERT] {severity}: {competitor_name} - {kci_name}",
        "severity": severity,
        "competitor": competitor_name,
        "trigger": trigger_reason,
        "action_required": "Review GoNano dealer territory defense and counter-pricing immediately."
    }

def dispatch_webhook_alert(webhook_url: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sends JSON alert payload to external Slack, Discord, or custom webhook."""
    if not webhook_url:
        return {"status": "error", "message": "No webhook URL provided."}
        
    title = alert_data.get("title") or f"[ALERT] {alert_data.get('severity', 'Notice')}: {alert_data.get('competitor', alert_data.get('target', 'Market Alert'))}"
    competitor = alert_data.get("competitor") or alert_data.get("target") or "Market Rival"
    severity = alert_data.get("severity") or alert_data.get("event") or "Medium"
    trigger = alert_data.get("trigger") or alert_data.get("event") or "Manual Test Alert"
    action = alert_data.get("action_required") or "Review GoNano dealer territory defense and counter-pricing immediately."
    ts = alert_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    slack_payload = {
        "text": f"*{title}*\n> **Competitor:** {competitor}\n> **Severity:** `{severity}`\n> **Trigger Event:** {trigger}\n> *Action:* {action}\n_Timestamp: {ts}_"
    }
    
    try:
        res = httpx.post(webhook_url, json=slack_payload, timeout=8.0)
        return {"status": "success", "status_code": res.status_code, "message": "Alert dispatched successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def dispatch_telegram_alert(bot_token: str, chat_id: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sends formatted alert message via Telegram Bot API."""
    if not bot_token or not chat_id:
        return {"status": "error", "message": "Missing Telegram bot token or chat ID."}
        
    text = (
        f"[ALERT] *[GONANO CRO ALERT // {alert_data['severity']}]*\n\n"
        f"• *Competitor:* {alert_data['competitor']}\n"
        f"• *Trigger:* {alert_data['trigger']}\n"
        f"• *Recommended Action:* {alert_data['action_required']}\n\n"
        f"[TIME] _{alert_data['timestamp']}_"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    try:
        res = httpx.post(url, json=payload, timeout=8.0)
        return {"status": "success", "status_code": res.status_code, "message": "Telegram alert sent."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
