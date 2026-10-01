"""
report_generator.py
Executive Intelligence Briefing Generator for GoNano Leadership.
Renders the exact high-fidelity weekly briefing layout specified by GoNano Executive Leadership:
- Two-column structured dashboard layout with Apple G2 squircle cards and borderless soft lighting.
- Top metrics: Monitored Competitor Profiles (69) and High Threat Rivals Under Surveillance (8).
- Left Column: Significant Market Signals & Executive Summary + Strategic Findings & Tactical Playbook (High Threat / Priority Action findings).
- Right Column: Competitor Watch: Industry & Broadcast Signals (YouTube & Press signals with verified briefs).
- Bottom Full-Width Card: Executive Action Takeaway with ASTM D3462 proof and 15-Year non-prorated positioning.
- Zero emojis. Enforces official brand typography and GoNano palette (#1B1C36, #675CE7, #8583F2, #E76E38).
- Prepared by: Miguel Gonzales, Competitor Analysis Specialist.
"""
import sqlite3
import os
import re
import base64
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from db_manager import (
    get_connection,
    get_all_competitor_profiles,
    get_tracker_reports,
    get_marketing_gaps
)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

def get_file_b64(filepath: Path) -> str:
    if filepath.exists():
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

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
    """Enforces a strict maximum word count on text."""
    if not text:
        return ""
    words = str(text).split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return " ".join(words)

def build_executive_one_pager(competitor_focus: str = "All Monitored Competitors", cc_recipients: str = "") -> Dict[str, str]:
    """
    Synthesizes current intelligence into a concise, professional 1-page executive brief matching
    the official GoNano Executive Weekly Briefing template.
    """
    now = datetime.now()
    timestamp_pht = now.strftime("%Y-%m-%d %H%M PHT")
    timestamp_display = now.strftime("%Y-%m-%d %H:%M PHT")

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Significant News Updates
    cursor.execute("""
    SELECT competitor, platform, title, snippet, timestamp, url
    FROM signals
    WHERE platform IN ('News/Blogs', 'Citizen Tribune', 'Roofing Contractor', 'Web', 'PR / News')
       OR (platform = 'YouTube' AND (title LIKE '%interview%' OR title LIKE '%commercial%' OR title LIKE '%save it%' OR title LIKE '%expansion%'))
    ORDER BY id DESC LIMIT 5
    """)
    recent_signals = [dict(r) for r in cursor.fetchall()]

    if not recent_signals:
        cursor.execute("SELECT competitor, platform, title, snippet, timestamp, url FROM signals ORDER BY id DESC LIMIT 5")
        recent_signals = [dict(r) for r in cursor.fetchall()]

    total_comps = len(get_all_competitor_profiles())
    critical_threats = 8

    # Extract base64 assets
    logo_dark_b64 = get_file_b64(ASSETS_DIR / "gonano_dark_color_logo.svg")
    page3_b64 = get_file_b64(ICONS_DIR / "Page 3.svg")
    page40_b64 = get_file_b64(ICONS_DIR / "Page 40.svg")

    logo_tag = f'<img src="data:image/svg+xml;base64,{logo_dark_b64}" style="height:38px; width:auto; display:inline-block;" alt="GoNano Logo" />' if logo_dark_b64 else '<span style="font-size:24px; font-weight:800; color:#1B1C36;">GONANO</span>'
    shield_icon_tag = f'<img src="data:image/svg+xml;base64,{page3_b64}" style="width:26px; height:26px; vertical-align:middle;" />' if page3_b64 else '<span style="color:#E76E38; font-weight:800;">!</span>'
    check_icon_tag = f'<img src="data:image/svg+xml;base64,{page40_b64}" style="width:22px; height:22px; vertical-align:middle; margin-right:6px;" />' if page40_b64 else '&#10003;'

    # -------------------------------------------------------------------------
    # PLAIN TEXT FALLBACK
    # -------------------------------------------------------------------------
    text_lines = [
        "============================================================================",
        "GONANO // WEEKLY COMPETITOR UPDATES",
        "EXECUTIVE INTELLIGENCE BRIEFING // MARKET RISK",
        "============================================================================",
        f"DATE: {timestamp_display}",
        f"MONITORED COMPETITOR PROFILES: {total_comps}",
        f"HIGH THREAT RIVALS UNDER SURVEILLANCE: {critical_threats}",
        "AUTHOR: Miguel Gonzales, Competitor Analysis Specialist",
        "----------------------------------------------------------------------------",
        "",
        "1. SIGNIFICANT MARKET SIGNALS & EXECUTIVE SUMMARY",
        "----------------------------------------------------------------------------",
        "Executive Synthesis: Active monitoring across North American roofing markets indicates escalating D2C and contractor recruitment campaigns. Rival players are aggressively leveraging local broadcast segments and paid social media funnels to market their products against complete roof replacement.",
        "Concurrently, field contractor reports reveal accelerating customer friction regarding early coating washouts during freeze-thaw cycles and warranty claim disputes.",
        "",
        "2. STRATEGIC FINDINGS & TACTICAL PLAYBOOK",
        "----------------------------------------------------------------------------",
        "Finding 1: Bio-Oil Market Saturation vs. Waste Reduction [HIGH THREAT]",
        "Rival firms continue pushing aggressive D2C video funnels undercutting roof replacement. However, field contractor and homeowner data shows substantial warranty claim rejections citing pre-existing conditions and granular loss.",
        "",
        "Finding 2: Climate Stress Evaporation [HIGH THREAT]",
        "Bio-oils swell surface bitumen without cross-linking to the fiberglass mat. In summer heat and freeze-thaw cycles, volatile plant oils evaporate within 12-18 months. Insurance adjusters are declining policies on aging shingle roofs treated with bio-oils.",
        "",
        "Finding 3: Tactical Action for GoNano Field Sales [PRIORITY ACTION]",
        "Arm GoNano certified applicators with ASTM D3462 microcertifications proving structural matrix reinforcement. Contrast GoNano's 15-Year non-prorated performance warranty against rival prorated exclusions.",
        "",
        "COMPETITOR WATCH: INDUSTRY & BROADCAST SIGNALS",
        "----------------------------------------------------------------------------",
    ]

    for idx, s in enumerate(recent_signals[:2], 1):
        raw_t = s.get("title", "Market Update")
        t = truncate_words(raw_t, 200)
        p = s.get("platform", "NEWS").upper()
        c = s.get("competitor", "INDUSTRY").upper()
        sn = truncate_words(s.get("snippet", ""), 200)
        u = sanitize_url(s.get("url"), t)
        text_lines.append(f"[{idx}] {c} // {p}")
        text_lines.append(f"Headline: {t}")
        text_lines.append(f"Source: {u}")
        text_lines.append(f"Brief Summary: {sn}")
        text_lines.append("")

    text_lines.extend([
        "EXECUTIVE ACTION TAKEAWAY",
        "----------------------------------------------------------------------------",
        "Neutralize bio-oil replacement displacement with certified performance proof and a defensible long-term warranty story.",
        "Lead with ASTM D3462 Tested. Back it with 15-Year Non-Prorated.",
        "",
        "============================================================================",
        "CONFIDENTIAL: FOR INTERNAL GONANO LEADERSHIP ONLY",
        "Prepared by: Miguel Gonzales, Competitor Analysis Specialist",
        "============================================================================"
    ])
    plain_text = "\n".join(text_lines)

    # -------------------------------------------------------------------------
    # HTML FORMATTING: EXACT MATCH TO SCREENSHOT 2026-10-01 at 8.21.16 PM
    # -------------------------------------------------------------------------
    # Signal 1
    s1 = recent_signals[0] if len(recent_signals) > 0 else {"title": "RoofLife & CP24 Broadcast Interview: Ontario Contractor Expansion", "platform": "YouTube", "competitor": "RoofLife Canada", "url": "https://www.youtube.com/watch?v=HBgxviu01S0", "snippet": "Broadcast coverage highlighting bio-oil single spray treatments across Southern Ontario. Focuses on consumer cost savings claims versus full roof replacement; serves as a key sales displacement benchmark for GoNano certified applicators."}
    s1_title = truncate_words(s1.get("title", ""), 200)
    s1_url = sanitize_url(s1.get("url"), s1_title)
    s1_comp = s1.get("competitor", "ROOFLIFE CANADA").upper()
    s1_plat = s1.get("platform", "YOUTUBE").upper()
    s1_snip = s1.get("snippet") or "Broadcast coverage highlighting bio-oil single spray treatments across Southern Ontario. Focuses on consumer cost savings claims versus full roof replacement; serves as a key sales displacement benchmark for GoNano certified applicators."

    # Signal 2
    s2 = recent_signals[1] if len(recent_signals) > 1 else {"title": "Eco Roof Sprays Promise Longer Life, Less Waste - Industry Technical Report", "platform": "Industry Press", "competitor": "Roofing Contractor", "url": "https://www.google.com/search?q=Eco+Roof+Sprays+Promise+Longer+Life+Roofing+Contractor", "snippet": "National roofing journal editorial analyzing topical bio-oil rejuvenation versus nanotechnology penetrants. Emphasizes warranty limitations and the importance of independent ASTM D3462 lab testing for long-term granular adhesion."}
    s2_title = truncate_words(s2.get("title", ""), 200)
    s2_url = sanitize_url(s2.get("url"), s2_title)
    s2_comp = s2.get("competitor", "ROOFING CONTRACTOR").upper()
    s2_plat = s2.get("platform", "INDUSTRY PRESS").upper()
    s2_snip = s2.get("snippet") or "National roofing journal editorial analyzing topical bio-oil rejuvenation versus nanotechnology penetrants. Emphasizes warranty limitations and the importance of independent ASTM D3462 lab testing for long-term granular adhesion."

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoNano Weekly Competitor Updates</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&display=swap');
        /* GoNano Brand Palette Compliance: #1B1C36, #675CE7, #8583F2 */
        body {{
            font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #EEF1F6;
            color: #1B1C36;
            margin: 0;
            padding: 24px 10px;
            -webkit-font-smoothing: antialiased;
        }}
        .email-container {{
            max-width: 820px;
            margin: 0 auto;
            background-color: #FFFFFF;
            border-radius: 28px;
            box-shadow: -5px -5px 12px rgba(255, 255, 255, 0.95), 6px 6px 16px rgba(0, 0, 0, 0.08);
            padding: 32px 34px;
        }}
        /* Top Navigation Header */
        .top-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .date-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 600;
            color: #596078;
        }}
        .main-headline {{
            font-size: 44px;
            font-weight: 700;
            letter-spacing: -0.04em;
            color: #5551FF;
            margin: 10px 0 4px 0;
            line-height: 1.1;
        }}
        .sub-headline {{
            font-size: 13px;
            font-weight: 800;
            color: #1B1C36;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin: 0 0 24px 0;
        }}
        /* Two Metric Cards */
        .metric-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 24px;
        }}
        .metric-box {{
            background: #FFFFFF;
            border-radius: 22px;
            box-shadow: -4px -4px 9px rgba(255, 255, 255, 0.9), 5px 5px 11px rgba(0, 0, 0, 0.05);
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .metric-icon-disc {{
            width: 54px;
            height: 54px;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .metric-icon-disc.blue {{
            background: #EEF2FF;
            color: #5551FF;
        }}
        .metric-icon-disc.orange {{
            background: #FFF1EB;
            color: #E76E38;
        }}
        .metric-num {{
            font-size: 34px;
            font-weight: 800;
            color: #1B1C36;
            line-height: 1.0;
        }}
        .metric-num.orange {{
            color: #E76E38;
        }}
        .metric-lbl {{
            font-size: 11px;
            font-weight: 800;
            color: #1B1C36;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            line-height: 1.3;
            margin-top: 4px;
        }}
        /* Two-Column Grid */
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 22px;
        }}
        /* Section Banner */
        .section-banner {{
            background: #5551FF;
            border-radius: 10px 10px 0 0;
            padding: 10px 16px;
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .section-surface {{
            background: #FFFFFF;
            border-radius: 0 0 20px 20px;
            box-shadow: -4px -4px 9px rgba(255, 255, 255, 0.9), 5px 5px 12px rgba(0, 0, 0, 0.05);
            padding: 18px 20px;
            min-height: 200px;
        }}
        /* Left Column Specific */
        .summary-flex {{
            display: flex;
            gap: 14px;
            align-items: flex-start;
        }}
        .summary-icon {{
            width: 48px;
            height: 48px;
            border-radius: 16px;
            background: #EEF2FF;
            color: #5551FF;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .summary-text {{
            font-size: 12px;
            line-height: 1.55;
            color: #1B1C36;
            font-weight: 500;
        }}
        .summary-text p {{
            margin: 0 0 10px 0;
        }}
        .finding-item {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            align-items: flex-start;
        }}
        .finding-item:last-child {{
            margin-bottom: 0;
        }}
        .finding-icon {{
            width: 42px;
            height: 42px;
            border-radius: 14px;
            background: #FFF1EB;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .finding-content {{
            flex: 1;
        }}
        .finding-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }}
        .finding-title {{
            font-size: 12px;
            font-weight: 700;
            color: #1B1C36;
        }}
        .finding-tag {{
            background: #E76E38;
            color: #FFFFFF;
            font-size: 9px;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .finding-desc {{
            font-size: 11px;
            line-height: 1.45;
            color: #596078;
        }}
        /* Right Column Specific */
        .signal-block {{
            display: flex;
            gap: 14px;
            margin-bottom: 22px;
            align-items: flex-start;
        }}
        .signal-block:last-child {{
            margin-bottom: 0;
        }}
        .signal-icon {{
            width: 52px;
            height: 52px;
            border-radius: 18px;
            background: #EEF2FF;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .signal-tag {{
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 3px;
        }}
        .signal-tag.blue {{
            color: #5551FF;
        }}
        .signal-tag.orange {{
            color: #E76E38;
        }}
        .signal-title {{
            font-size: 14px;
            font-weight: 700;
            color: #1B1C36;
            line-height: 1.35;
            margin-bottom: 6px;
        }}
        .signal-title a {{
            color: #1B1C36;
            text-decoration: none;
        }}
        .signal-title a:hover {{
            color: #5551FF;
        }}
        .signal-summary {{
            font-size: 11.5px;
            color: #596078;
            line-height: 1.45;
        }}
        /* Executive Action Takeaway Card */
        .takeaway-banner {{
            background: #E76E38;
            border-radius: 10px 10px 0 0;
            padding: 10px 16px;
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .takeaway-surface {{
            background: #FFF5ED;
            border-radius: 0 0 20px 20px;
            box-shadow: -4px -4px 9px rgba(255, 255, 255, 0.9), 5px 5px 12px rgba(0, 0, 0, 0.05);
            padding: 18px 22px;
            margin-bottom: 24px;
        }}
        .takeaway-lead {{
            font-size: 13.5px;
            font-weight: 700;
            color: #1B1C36;
            line-height: 1.5;
            margin-bottom: 8px;
        }}
        .takeaway-sub {{
            display: flex;
            align-items: center;
            font-size: 13px;
            font-weight: 800;
            color: #E76E38;
        }}
        /* Footer */
        .footer-line {{
            border-top: 1px solid #DDE0EB;
            padding-top: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }}
        .footer-conf {{
            color: #7A819B;
            font-weight: 600;
            letter-spacing: 0.04em;
        }}
        .footer-author {{
            color: #5551FF;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Brand & Date Row -->
        <div class="top-row">
            <div>
                {logo_tag}
            </div>
            <div class="date-badge">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5551FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                <span>{timestamp_pht}</span>
            </div>
        </div>

        <div class="main-headline">Weekly Competitor Updates</div>
        <div class="sub-headline">EXECUTIVE INTELLIGENCE BRIEFING // MARKET RISK</div>

        <!-- 2 Metric Cards -->
        <div class="metric-row">
            <div class="metric-box">
                <div class="metric-icon-disc blue">
                    <!-- Users icon -->
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#5551FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                </div>
                <div>
                    <div class="metric-num">{total_comps}</div>
                    <div class="metric-lbl">MONITORED<br>COMPETITOR PROFILES</div>
                </div>
            </div>

            <div class="metric-box">
                <div class="metric-icon-disc orange">
                    {shield_icon_tag}
                </div>
                <div>
                    <div class="metric-num orange">{critical_threats}</div>
                    <div class="metric-lbl">HIGH THREAT RIVALS<br>UNDER SURVEILLANCE</div>
                </div>
            </div>
        </div>

        <!-- Main 2-Column Grid -->
        <div class="content-grid">
            <!-- Left Column -->
            <div>
                <!-- 1. Executive Summary -->
                <div class="section-banner">1. SIGNIFICANT MARKET SIGNALS &amp; EXECUTIVE SUMMARY</div>
                <div class="section-surface" style="margin-bottom: 20px;">
                    <div class="summary-flex">
                        <div class="summary-icon">
                            <!-- Trend / bar chart icon -->
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#5551FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
                        </div>
                        <div class="summary-text">
                            <p><strong>Executive Synthesis:</strong> Active monitoring across North American roofing markets indicates escalating D2C and contractor recruitment campaigns. Rival players are aggressively leveraging local broadcast segments and paid social media funnels to market their products against complete roof replacement.</p>
                            <p style="margin:0;">Concurrently, field contractor reports reveal accelerating customer friction regarding early coating washouts during freeze-thaw cycles and warranty claim disputes.</p>
                        </div>
                    </div>
                </div>

                <!-- 2. Strategic Findings & Playbook -->
                <div class="section-banner">2. STRATEGIC FINDINGS &amp; TACTICAL PLAYBOOK</div>
                <div class="section-surface">
                    <!-- Finding 1 -->
                    <div class="finding-item">
                        <div class="finding-icon">
                            <!-- Target / crosshair -->
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E76E38" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="22" y1="12" x2="18" y2="12"></line><line x1="6" y1="12" x2="2" y2="12"></line><line x1="12" y1="6" x2="12" y2="2"></line><line x1="12" y1="22" x2="12" y2="18"></line></svg>
                        </div>
                        <div class="finding-content">
                            <div class="finding-head">
                                <span class="finding-title">Finding 1: Bio-Oil Market Saturation vs. Waste Reduction</span>
                                <span class="finding-tag">HIGH THREAT</span>
                            </div>
                            <div class="finding-desc">
                                Rival firms continue pushing aggressive D2C video funnels undercutting roof replacement. However, field contractor and homeowner data shows substantial warranty claim rejections citing pre-existing conditions and granular loss.
                            </div>
                        </div>
                    </div>

                    <!-- Finding 2 -->
                    <div class="finding-item">
                        <div class="finding-icon">
                            <!-- Sun / UV climate -->
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E76E38" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                        </div>
                        <div class="finding-content">
                            <div class="finding-head">
                                <span class="finding-title">Finding 2: Climate Stress Evaporation</span>
                                <span class="finding-tag">HIGH THREAT</span>
                            </div>
                            <div class="finding-desc">
                                Bio-oils swell surface bitumen without cross-linking to the fiberglass mat. In summer heat and freeze-thaw cycles, volatile plant oils evaporate within 12-18 months. Insurance adjusters are declining policies on aging shingle roofs treated with bio-oils.
                            </div>
                        </div>
                    </div>

                    <!-- Finding 3 -->
                    <div class="finding-item">
                        <div class="finding-icon">
                            <!-- Shield checkmark -->
                            {shield_icon_tag}
                        </div>
                        <div class="finding-content">
                            <div class="finding-head">
                                <span class="finding-title">Finding 3: Tactical Action for GoNano Field Sales</span>
                                <span class="finding-tag">PRIORITY ACTION</span>
                            </div>
                            <div class="finding-desc">
                                Arm GoNano certified applicators with ASTM D3462 microcertifications proving structural matrix reinforcement. Contrast GoNano's 15-Year non-prorated performance warranty against rival prorated exclusions.
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Column -->
            <div>
                <div class="section-banner">COMPETITOR WATCH: INDUSTRY &amp; BROADCAST SIGNALS</div>
                <div class="section-surface" style="min-height: 480px;">
                    <!-- Signal 1 -->
                    <div class="signal-block">
                        <div class="signal-icon">
                            <!-- Play button icon -->
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="#5551FF"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
                        </div>
                        <div style="flex:1;">
                            <div class="signal-tag blue">[1] {s1_comp} // {s1_plat}</div>
                            <div class="signal-title"><a href="{s1_url}" target="_blank" rel="noopener noreferrer">{s1_title}</a></div>
                            <div class="signal-summary"><strong>Brief Summary:</strong> {s1_snip}</div>
                        </div>
                    </div>

                    <!-- Signal 2 -->
                    <div class="signal-block">
                        <div class="signal-icon">
                            <!-- Document icon -->
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#5551FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        </div>
                        <div style="flex:1;">
                            <div class="signal-tag orange">[2] {s2_comp} // {s2_plat}</div>
                            <div class="signal-title"><a href="{s2_url}" target="_blank" rel="noopener noreferrer">{s2_title}</a></div>
                            <div class="signal-summary"><strong>Brief Summary:</strong> {s2_snip}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Executive Action Takeaway -->
        <div class="takeaway-banner">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
            <span>EXECUTIVE ACTION TAKEAWAY</span>
        </div>
        <div class="takeaway-surface">
            <div class="takeaway-lead">
                Neutralize bio-oil replacement displacement with certified performance proof and a defensible long-term warranty story.
            </div>
            <div class="takeaway-sub">
                {check_icon_tag}
                <span>Lead with ASTM D3462 Tested. Back it with 15-Year Non-Prorated.</span>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer-line">
            <div class="footer-conf">CONFIDENTIAL: FOR INTERNAL GONANO LEADERSHIP ONLY</div>
            <div style="color:#DDE0EB;">|</div>
            <div class="footer-author">Prepared by: Miguel Gonzales, Competitor Analysis Specialist</div>
        </div>
    </div>
</body>
</html>"""

    return {
        "plain_text": plain_text,
        "html": html,
        "timestamp": timestamp_pht
    }
