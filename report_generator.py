"""
report_generator.py
Weekly Competitor Updates email for GoNano leadership.

Everything in the email comes from data the scan collected this week:
- Metric cards: tracked competitors (test rows excluded) and news items that passed the relevance check.
- Left column: a factual summary of what the scan found, and where to find more.
- Right column: up to four news items. An item is kept only when it names a tracked competitor
  and is about roofing; test entries are never shown.
- No fixed findings, no product or warranty claims, and no placeholder news. If nothing passes
  the check, the email says so.

Email HTML uses inline CSS and nested tables so it renders in Gmail, Outlook and Apple Mail.
Brand palette: #1B1C36, #675CE7, #8583F2, #E76E38, #5551FF.
Author: Miguel Gonzales, Competitor Analysis Specialist.
"""
import html as _html
import os
import re
import urllib.parse
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, List
from db_manager import get_connection, get_all_competitor_profiles

CDN_BASE = "https://cdn.jsdelivr.net/gh/mglcrlo18/GoNano-Competitor-Intelligence-Tool-For-Certified-Contractors@main/assets"
MAX_NEWS_ITEMS = 4

# Rows that are QA fixtures or working notes, not competitors.
_TEST_NAME_RE = re.compile(r"(^|[^a-z])qa([^a-z]|$)|qa_|test|verification|competitor analysis|imposter", re.I)
# The item must be about roofing (English or French terms).
_ROOF_RE = re.compile(r"\b(roof\w*|shingle\w*|rejuven\w*|toit\w*|bardeau\w*|coating\w*|seal(?:ant|er)\w*)\b", re.I)
# Name fragments too generic to identify a competitor on their own.
_GENERIC = {"roof", "roofs", "roofing", "coating", "coatings", "nano", "quebec", "canada", "florida",
            "usa", "inc", "llc", "the", "solutions", "your brand"}


def sanitize_url(raw_url: str, fallback_title: str = "") -> str:
    if not raw_url or str(raw_url).strip() in ["#", "", "about:blank", "javascript:void(0)", "None"]:
        if fallback_title.strip():
            return f"https://www.google.com/search?q={urllib.parse.quote(fallback_title.strip())}"
        return "https://www.google.com/search?q=GoNano+roof+rejuvenation"
    cleaned = str(raw_url).strip()
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    return f"https://www.google.com/search?q={urllib.parse.quote(fallback_title.strip() or 'GoNano')}"


def truncate_words(text: str, max_words: int = 200) -> str:
    if not text:
        return ""
    words = str(text).split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return " ".join(words)


def _clean_text(val: str) -> str:
    if not val:
        return ""
    txt = re.sub(r"<[^>]+>", " ", str(val))
    txt = txt.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    return " ".join(txt.split())


def is_test_entry(name: str) -> bool:
    """True for QA fixtures and working-note rows such as 'QA_Verification_Brand_2026'."""
    return bool(_TEST_NAME_RE.search(name or ""))


def name_variants(name: str) -> List[str]:
    """Distinctive ways a competitor can be named, e.g. 'NoxNano (Noxor)' -> NoxNano, Noxor."""
    raw = str(name or "")
    parts = re.split(r"[/()\[\],]| - ", raw)
    candidates = {p.strip() for p in parts if p.strip()}
    base = re.sub(r"\(.*?\)", "", raw).strip()
    if base:
        candidates.add(base)
    out = []
    for c in candidates:
        c = " ".join(c.split())
        if len(c) >= 4 and c.lower() not in _GENERIC:
            out.append(c)
    return sorted(out, key=len, reverse=True)


def mentions_competitor(name: str, text: str) -> bool:
    low = (text or "").lower()
    for v in name_variants(name):
        if re.search(r"(?<![a-z0-9])" + re.escape(v.lower()) + r"(?![a-z0-9])", low):
            return True
    return False


def is_relevant_item(item: Dict[str, Any]) -> bool:
    """Keep an item only when it names its competitor and is about roofing."""
    comp = str(item.get("competitor") or "").strip()
    if not comp or is_test_entry(comp):
        return False
    text = f"{_clean_text(item.get('title'))} {_clean_text(item.get('snippet'))}"
    if not mentions_competitor(comp, text):
        return False
    # Look for roofing words outside the brand name itself ("Roof Maxx" alone does not make a story about roofing).
    rest = text
    for v in name_variants(comp):
        rest = re.sub(re.escape(v), " ", rest, flags=re.I)
    return bool(_ROOF_RE.search(rest))


def select_news(rows: List[Dict[str, Any]], limit: int = MAX_NEWS_ITEMS) -> Dict[str, Any]:
    """Filter scan rows to relevant, de-duplicated items, one per competitor first."""
    relevant, seen_titles = [], set()
    for r in rows:
        if not is_relevant_item(r):
            continue
        key = re.sub(r"\W+", " ", _clean_text(r.get("title")).lower()).strip()
        if not key or key in seen_titles:
            continue
        seen_titles.add(key)
        relevant.append(r)
    picked, used = [], set()
    for r in relevant:  # one item per competitor first
        c = r["competitor"].strip()
        if c not in used:
            used.add(c)
            picked.append(r)
        if len(picked) == limit:
            break
    for r in relevant:  # then fill remaining slots
        if len(picked) == limit:
            break
        if r not in picked:
            picked.append(r)
    return {"items": picked, "relevant": relevant, "dropped": max(0, len(rows) - len(relevant))}


def _e(s: Any) -> str:
    return _html.escape(str(s or ""), quote=True)


def build_executive_one_pager(competitor_focus: str = "All Monitored Competitors", cc_recipients: str = "") -> Dict[str, str]:
    now_utc = datetime.now(timezone.utc)
    now_est = now_utc.astimezone(ZoneInfo("America/New_York"))
    now_pht = now_utc.astimezone(ZoneInfo("Asia/Manila"))

    timestamp_badge = f"{now_est.strftime('%Y-%m-%d %H:%M %Z')} / {now_pht.strftime('%Y-%m-%d %H:%M')} PHT"
    date_ddmmyyyy = now_pht.strftime("%d/%m/%Y")
    cutoff_date = (now_pht - timedelta(days=7)).strftime("%Y-%m-%d")
    today_date = now_pht.strftime("%Y-%m-%d")

    # News scanned in the last 7 days (YouTube and Google News redirect links excluded as before)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT competitor, platform, title, snippet, timestamp, url
    FROM signals
    WHERE LOWER(platform) != 'youtube'
      AND timestamp >= ? AND timestamp <= ?
      AND url NOT LIKE '%news.google.com/rss/%'
    ORDER BY timestamp DESC, id DESC LIMIT 400
    """, (cutoff_date, today_date))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    news = select_news(rows)
    items = news["items"]
    n_relevant = len(news["relevant"])
    comps_named = sorted({r["competitor"].strip() for r in news["relevant"]})
    dropped = news["dropped"]

    tracked = [p for p in get_all_competitor_profiles()
               if p.get("name") and not is_test_entry(p["name"]) and "your brand" not in p["name"].lower()]
    total_comps = len(tracked)

    dashboard_url = (os.getenv("DASHBOARD_URL") or "").strip()
    logo_dark_url = f"{CDN_BASE}/gonano_logo_dark.png"
    icon_calendar = f"{CDN_BASE}/icons_png/page_34.png"
    window = f"{cutoff_date} to {today_date}"

    # ---- factual summary lines ----
    if n_relevant:
        s_found = (f"{n_relevant} news item{'s' if n_relevant != 1 else ''} about "
                   f"{len(comps_named)} tracked competitor{'s' if len(comps_named) != 1 else ''} passed the check for {window}.")
        s_named = "Named: " + ", ".join(comps_named[:8]) + ("." if len(comps_named) <= 8 else f", and {len(comps_named) - 8} more.")
    else:
        s_found = f"No news item about a tracked competitor passed the check for {window}."
        s_named = "The scan will run again next week."
    s_dropped = (f"{dropped} other item{'s' if dropped != 1 else ''} from the scan {'were' if dropped != 1 else 'was'} left out "
                 "because they did not name a tracked competitor or were not about roofing." if dropped else "")

    # ---- plain text ----
    text_lines = [
        "============================================================================",
        "GONANO // WEEKLY COMPETITOR UPDATES",
        "============================================================================",
        f"DATE: {timestamp_badge}",
        f"TRACKED COMPETITORS: {total_comps}",
        f"NEWS ITEMS THAT PASSED THE CHECK THIS WEEK: {n_relevant}",
        "----------------------------------------------------------------------------",
        "",
        "1. THIS WEEK AT A GLANCE",
        "----------------------------------------------------------------------------",
        s_found,
        s_named,
    ]
    if s_dropped:
        text_lines.append(s_dropped)
    text_lines += [
        "",
        "2. WHERE TO FIND MORE",
        "----------------------------------------------------------------------------",
        "In the Competitor Report Tracker (Google Sheets)" + (f", {dashboard_url}" if dashboard_url else "") + ":",
        "- News: approved news items",
        "- Ad Activity: active ads by brand",
        "- Coverage: GoNano locations and competitor dealers by state and province",
        "Full competitor profiles are emailed separately as they are completed.",
        "",
        f"COMPETITOR NEWS ({window})",
        "----------------------------------------------------------------------------",
    ]
    if items:
        for i, r in enumerate(items, 1):
            title = truncate_words(_clean_text(r.get("title")), 60)
            text_lines += [
                f"[{i}] {r['competitor'].strip().upper()} // {str(r.get('platform') or 'Source').upper()} ({r.get('timestamp') or ''})",
                f"Headline: {title}",
                f"Source: {sanitize_url(r.get('url'), title)}",
                f"Summary: {truncate_words(_clean_text(r.get('snippet')), 60)}",
                "",
            ]
    else:
        text_lines += ["No verified competitor news this week.", ""]
    text_lines += [
        "News is matched automatically by competitor name and roofing terms. Open the source before quoting it.",
        "============================================================================",
        "CONFIDENTIAL: FOR INTERNAL GONANO LEADERSHIP ONLY",
        "Prepared by: Miguel Gonzales, Competitor Analysis Specialist",
        "============================================================================",
    ]
    plain_text = "\n".join(text_lines)

    # ---- HTML pieces ----
    font = "font-family: 'Montserrat', Arial, Helvetica, sans-serif;"
    if items:
        news_blocks = []
        for i, r in enumerate(items, 1):
            title = truncate_words(_clean_text(r.get("title")), 60)
            url = sanitize_url(r.get("url"), title)
            colour = "#5551FF" if i % 2 else "#E76E38"
            news_blocks.append(f"""
                                                    <div style="margin-bottom: 22px;">
                                                        <div style="{font} font-size: 11px; font-weight: 800; color: {colour}; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;">
                                                            [{i}] {_e(r['competitor'].strip())} // {_e(r.get('platform') or 'Source')} &nbsp;&bull;&nbsp; {_e(r.get('timestamp') or '')}
                                                        </div>
                                                        <div style="{font} font-size: 14px; font-weight: 700; line-height: 1.35; margin-bottom: 6px;">
                                                            <a href="{_e(url)}" target="_blank" style="color: #1B1C36; text-decoration: none;">{_e(title)}</a>
                                                        </div>
                                                        <div style="{font} font-size: 12px; line-height: 1.5; color: #596078;">
                                                            <strong>Summary:</strong> {_e(truncate_words(_clean_text(r.get('snippet')), 60))}
                                                        </div>
                                                    </div>""")
        news_html = "".join(news_blocks)
    else:
        news_html = f"""
                                                    <div style="{font} font-size: 13px; line-height: 1.6; color: #1B1C36;">
                                                        No verified competitor news this week.
                                                    </div>"""

    tracker_label = (f'<a href="{_e(dashboard_url)}" target="_blank" style="color: #5551FF; font-weight: 700;">Competitor Report Tracker</a>'
                     if dashboard_url else "<strong>Competitor Report Tracker</strong> (Google Sheets)")
    dropped_html = f'<p style="margin: 0; color: #596078;">{_e(s_dropped)}</p>' if s_dropped else ""

    html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>GoNano Weekly Competitor Updates</title>
    <style type="text/css">
        /* Brand Colors: #1B1C36, #675CE7, #8583F2, #E76E38, #5551FF */
        body {{ margin: 0; padding: 0; background-color: #EEF1F6; -webkit-font-smoothing: antialiased; }}
        table {{ border-collapse: collapse; mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        td {{ border-collapse: collapse; }}
        img {{ border: 0; outline: none; text-decoration: none; display: block; }}
        a {{ text-decoration: none; color: #1B1C36; }}
    </style>
</head>
<body bgcolor="#EEF1F6" style="margin: 0; padding: 24px 0; background-color: #EEF1F6; {font}">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#EEF1F6" style="background-color: #EEF1F6; margin: 0; padding: 24px 0;">
        <tr>
            <td align="center" valign="top">
                <table width="780" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFFFFF" style="width: 780px; max-width: 780px; background-color: #FFFFFF; border-radius: 26px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); padding: 34px 38px;">

                    <!-- 1. HEADER ROW: LOGO & DATE -->
                    <tr>
                        <td valign="top" style="padding-bottom: 10px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="left" valign="middle">
                                        <img src="{logo_dark_url}" width="175" height="44" alt="GoNano" style="display: block; width: 175px; height: auto;" />
                                    </td>
                                    <td align="right" valign="middle">
                                        <table cellpadding="0" cellspacing="0" border="0" bgcolor="#F4F6FB" style="background-color: #F4F6FB; border-radius: 8px; padding: 6px 14px;">
                                            <tr>
                                                <td valign="middle" style="padding-right: 6px;">
                                                    <img src="{icon_calendar}" width="16" height="16" alt="Date" style="display: block; width: 16px; height: 16px;" />
                                                </td>
                                                <td valign="middle" style="{font} font-size: 12px; font-weight: 600; color: #596078; white-space: nowrap;">
                                                    {timestamp_badge}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- 2. HEADLINE -->
                    <tr>
                        <td valign="top" style="padding-bottom: 22px;">
                            <div style="{font} font-size: 46px; font-weight: 700; color: #5551FF; letter-spacing: -0.04em; line-height: 1.12; margin: 0 0 6px 0;">
                                Weekly Competitor Updates
                            </div>
                            <div style="{font} font-size: 13px; font-weight: 800; color: #1B1C36; letter-spacing: 0.12em; text-transform: uppercase; margin: 0;">
                                WHAT THE SCAN FOUND THIS WEEK
                            </div>
                        </td>
                    </tr>

                    <!-- 3. METRIC CARDS -->
                    <tr>
                        <td valign="top" style="padding-bottom: 24px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td width="48%" valign="top" bgcolor="#FFFFFF" style="background-color: #FFFFFF; border: 1px solid #EBEFFA; border-radius: 20px; padding: 18px 24px;">
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td width="70" valign="middle">
                                                    <div style="{font} font-size: 44px; font-weight: 800; color: #5551FF; line-height: 1.0;">{total_comps}</div>
                                                </td>
                                                <td valign="middle" style="padding-left: 8px;">
                                                    <div style="{font} font-size: 11px; font-weight: 800; color: #1B1C36; text-transform: uppercase; letter-spacing: 0.05em; line-height: 1.35;">
                                                        TRACKED<br />COMPETITORS
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                    <td width="4%">&nbsp;</td>
                                    <td width="48%" valign="top" bgcolor="#FFFFFF" style="background-color: #FFFFFF; border: 1px solid #FDEEE6; border-radius: 20px; padding: 18px 24px;">
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td width="70" valign="middle">
                                                    <div style="{font} font-size: 44px; font-weight: 800; color: #E76E38; line-height: 1.0;">{n_relevant}</div>
                                                </td>
                                                <td valign="middle" style="padding-left: 8px;">
                                                    <div style="{font} font-size: 11px; font-weight: 800; color: #E76E38; text-transform: uppercase; letter-spacing: 0.05em; line-height: 1.35;">
                                                        VERIFIED NEWS ITEMS<br />THIS WEEK
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- 4. TWO-COLUMN GRID -->
                    <tr>
                        <td valign="top" style="padding-bottom: 24px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <!-- LEFT COLUMN -->
                                    <td width="48%" valign="top">
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 22px;">
                                            <tr>
                                                <td bgcolor="#5551FF" style="background-color: #5551FF; border-radius: 10px 10px 0 0; padding: 10px 16px; {font} font-size: 11px; font-weight: 800; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.06em;">
                                                    1. THIS WEEK AT A GLANCE
                                                </td>
                                            </tr>
                                            <tr>
                                                <td bgcolor="#FFFFFF" style="background-color: #FFFFFF; border: 1px solid #EBEFFA; border-top: none; border-radius: 0 0 18px 18px; padding: 20px 22px;">
                                                    <div style="{font} font-size: 12.5px; line-height: 1.6; color: #1B1C36;">
                                                        <p style="margin: 0 0 10px 0;">{_e(s_found)}</p>
                                                        <p style="margin: 0 0 10px 0;">{_e(s_named)}</p>
                                                        {dropped_html}
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>

                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td bgcolor="#5551FF" style="background-color: #5551FF; border-radius: 10px 10px 0 0; padding: 10px 16px; {font} font-size: 11px; font-weight: 800; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.06em;">
                                                    2. WHERE TO FIND MORE
                                                </td>
                                            </tr>
                                            <tr>
                                                <td bgcolor="#FFFFFF" style="background-color: #FFFFFF; border: 1px solid #EBEFFA; border-top: none; border-radius: 0 0 18px 18px; padding: 20px 22px;">
                                                    <div style="{font} font-size: 12.5px; line-height: 1.6; color: #1B1C36;">
                                                        <p style="margin: 0 0 8px 0;">{tracker_label}:</p>
                                                        <p style="margin: 0 0 4px 0;"><strong>News:</strong> approved news items</p>
                                                        <p style="margin: 0 0 4px 0;"><strong>Ad Activity:</strong> active ads by brand</p>
                                                        <p style="margin: 0 0 10px 0;"><strong>Coverage:</strong> GoNano locations and competitor dealers by state and province</p>
                                                        <p style="margin: 0; color: #596078;">Full competitor profiles are emailed separately as they are completed.</p>
                                                    </div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>

                                    <td width="4%">&nbsp;</td>

                                    <!-- RIGHT COLUMN -->
                                    <td width="48%" valign="top">
                                        <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                            <tr>
                                                <td bgcolor="#5551FF" style="background-color: #5551FF; border-radius: 10px 10px 0 0; padding: 10px 16px; {font} font-size: 11px; font-weight: 800; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.06em;">
                                                    COMPETITOR NEWS ({window})
                                                </td>
                                            </tr>
                                            <tr>
                                                <td bgcolor="#FFFFFF" style="background-color: #FFFFFF; border: 1px solid #EBEFFA; border-top: none; border-radius: 0 0 18px 18px; padding: 22px 22px 4px 22px;">{news_html}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- 5. FOOTER -->
                    <tr>
                        <td valign="top" style="border-top: 1px solid #EBEFFA; padding-top: 16px;">
                            <div style="{font} font-size: 10.5px; line-height: 1.5; color: #7A819B; margin-bottom: 10px;">
                                News is matched automatically by competitor name and roofing terms. Open the source before quoting it.
                            </div>
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="left" valign="middle" style="{font} font-size: 11px; font-weight: 700; color: #5551FF;">
                                        Prepared by: Miguel Gonzales,<br />Competitor Analysis Specialist
                                    </td>
                                    <td align="right" valign="middle" style="{font} font-size: 10.5px; font-weight: 600; color: #7A819B; letter-spacing: 0.04em;">
                                        CONFIDENTIAL: FOR INTERNAL GONANO LEADERSHIP ONLY
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return {
        "plain_text": plain_text,
        "html": html,
        "timestamp": timestamp_badge,
        "date_ddmmyyyy": date_ddmmyyyy,
        "subject": f"Competitor Updates as of {date_ddmmyyyy}",
    }
