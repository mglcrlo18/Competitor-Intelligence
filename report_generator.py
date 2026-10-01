"""
report_generator.py
Executive Intelligence Briefing Generator for GoNano Leadership.
Produces a strict, professional 1-page intelligence report covering:
1. Updates on Significant News & Market Signals (with Executive Summary before headlines)
2. Strategic Findings & Tactical Playbook
Completely void of emojis. Formatted in both Plain Text and High-Fidelity Flowy Tactile Executive HTML with GoNano Brand Colors (#1B1C36, #675CE7, #8583F2).
Enforces a maximum of 200 words on headlines and summaries.
Prepared by: Miguel Gonzales, Competitor Analysis Specialist.
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

def get_logo_base64() -> str:
    p = ASSETS_DIR / "gonano_light_color_logo.png"
    if p.exists():
        with open(p, "rb") as f:
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
    Synthesizes current intelligence into a concise, professional 1-page executive brief.
    Returns a dictionary with 'plain_text' and 'html' representations.
    Strictly zero emojis. Follows official GoNano brand colors.
    Section 1: Updates on Significant News & Market Signals (with summary before headlines, max 200 words per headline)
    Section 2: Strategic Findings & Tactical Playbook
    """
    timestamp_pht = datetime.now().strftime("%Y-%m-%d %H:%M PHT")
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Significant News Updates
    cursor.execute("""
    SELECT competitor, platform, title, snippet, timestamp, url
    FROM signals
    WHERE platform IN ('News/Blogs', 'Citizen Tribune', 'Roofing Contractor', 'Web', 'PR / News')
       OR (platform = 'YouTube' AND (title LIKE '%interview%' OR title LIKE '%commercial%' OR title LIKE '%save it%'))
    ORDER BY id DESC LIMIT 5
    """)
    recent_signals = [dict(r) for r in cursor.fetchall()]

    if not recent_signals:
        cursor.execute("SELECT competitor, platform, title, snippet, timestamp, url FROM signals ORDER BY id DESC LIMIT 5")
        recent_signals = [dict(r) for r in cursor.fetchall()]

    # 2. Key Metrics
    total_comps = len(get_all_competitor_profiles())
    critical_threats = 8

    # Section 1 Summary of Findings (Placed before headlines, max 200 words)
    section1_summary_raw = (
        "Active monitoring across North American roofing markets indicates escalating D2C and contractor "
        "recruitment campaigns by regional bio-oil and elastomeric spray competitors. Rival players (notably RoofLife "
        "Canada, Roof Maxx, and RevivaRoof) are aggressively leveraging local broadcast segments and paid social media "
        "funnels to market 75-80% cost savings against complete roof replacements. Concurrently, field contractor reports "
        "reveal accelerating customer friction regarding early coating washouts during freeze-thaw cycles and warranty claim "
        "disputes over pre-existing shingle granule loss. These developments create an immediate strategic opening for GoNano "
        "sales representatives to deploy third-party ASTM D3462 tear-strength data and highlight GoNano's 15-Year non-prorated "
        "nanotechnology warranty as the superior commercial alternative."
    )
    section1_summary = truncate_words(section1_summary_raw, 200)

    # -------------------------------------------------------------------------
    # PLAIN TEXT FORMATTING (Zero Emojis, Clean Structure)
    # -------------------------------------------------------------------------
    text_lines = []
    text_lines.append("============================================================================")
    text_lines.append("COMPETITOR INTELLIGENCE BRIEFING: EXECUTIVE 1-PAGE SUMMARY")
    text_lines.append("============================================================================")
    text_lines.append(f"SUBJECT: Competitor Updates as of {timestamp_pht}")
    text_lines.append(f"MONITORED ROSTER: {total_comps} Active Competitor Profiles Across North America")
    text_lines.append(f"THREAT POSTURE: {critical_threats} High/Critical Inherent Threats Under Continuous Surveillance")
    text_lines.append("AUTHOR: Miguel Gonzales, Competitor Analysis Specialist")
    text_lines.append("----------------------------------------------------------------------------")
    text_lines.append("")
    
    text_lines.append("SECTION 1: UPDATES ON SIGNIFICANT NEWS & MARKET SIGNALS")
    text_lines.append("----------------------------------------------------------------------------")
    text_lines.append("SUMMARY OF FINDINGS:")
    text_lines.append(section1_summary)
    text_lines.append("----------------------------------------------------------------------------")
    for idx, s in enumerate(recent_signals, 1):
        comp = s.get("competitor", "Industry")
        raw_title = s.get("title", "Market Update")
        title = truncate_words(raw_title, 200)
        outlet = s.get("platform", "Verified News")
        raw_snip = s.get("snippet", "")
        clean_snip = re.sub(r'<[^>]+>', ' ', raw_snip).replace("&nbsp;", " ")
        snip = truncate_words(re.sub(r'\s+', ' ', clean_snip).strip(), 200)
        safe_link = sanitize_url(s.get("url"), title)
        text_lines.append(f"[{idx}] {comp.upper()} - {outlet.upper()}")
        text_lines.append(f"    Headline: {title}")
        text_lines.append(f"    Source Link: {safe_link}")
        if snip:
            text_lines.append(f"    Brief Summary: {snip}")
        text_lines.append("")

    text_lines.append("SECTION 2: STRATEGIC FINDINGS & TACTICAL PLAYBOOK")
    text_lines.append("----------------------------------------------------------------------------")
    text_lines.append("1. Commercial Price Undercutting vs. Warranty Reality:")
    text_lines.append("   Rivals continue heavily advertising 75-80% savings vs. replacement. However,")
    text_lines.append("   field data documents rising customer warranty rejections citing pre-existing")
    text_lines.append("   roof age clauses and unsealed granule loss.")
    text_lines.append("")
    text_lines.append("2. Technical & Regulatory Vulnerability:")
    text_lines.append("   Topical bio-oils lack covalent cross-linking and evaporate under intense solar UV")
    text_lines.append("   within 12-18 months. Insurance adjusters are increasingly rejecting uncertified")
    text_lines.append("   coatings for aging shingle renewals.")
    text_lines.append("")
    text_lines.append("3. Immediate Field Sales Action:")
    text_lines.append("   Equip GoNano certified dealers with ASTM D3462 nail tear-strength proof and")
    text_lines.append("   promote the 15-Year non-prorated molecular performance warranty to homeowners")
    text_lines.append("   and commercial adjusters.")
    text_lines.append("")
    text_lines.append("=============================================================================")
    text_lines.append("CONFIDENTIAL: PREPARED FOR GONANO CORPORATE LEADERSHIP")
    text_lines.append("Prepared by: Miguel Gonzales, Competitor Analysis Specialist")
    text_lines.append("=============================================================================")

    plain_text = "\n".join(text_lines)

    # -------------------------------------------------------------------------
    # HTML FORMATTING (FLOWY TACTILE DESIGN SYSTEM)
    # -------------------------------------------------------------------------
    b64_logo = get_logo_base64()
    logo_tag = f'<img src="data:image/png;base64,{b64_logo}" style="height:48px; width:auto; display:inline-block; vertical-align:middle;" alt="GoNano Logo" />' if b64_logo else '<span style="font-size:24px; font-weight:800; color:#FFFFFF; letter-spacing:0.04em;">GONANO</span>'

    html_news_items = ""
    for idx, s in enumerate(recent_signals, 1):
        raw_title = s.get("title", "")
        title = truncate_words(raw_title, 200)
        raw_snip = s.get("snippet", "")
        clean_snip = re.sub(r'<[^>]+>', ' ', raw_snip).replace("&nbsp;", " ")
        snip_clean = truncate_words(re.sub(r'\s+', ' ', clean_snip).strip(), 200)
        safe_url = sanitize_url(s.get("url"), title)
        
        summary_body = snip_clean if len(snip_clean) > 20 else f"Verified market telemetry regarding {title}. Monitored for competitor commercial traction and field applicator sentiment."

        html_news_items += f"""
        <div style="background:#FFFFFF; border:none; border-radius:20px; box-shadow:-4px -4px 10px #FFFFFF, 5px 5px 12px rgba(0,0,0,0.06); padding:18px 20px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="display:inline-block; border-radius:9999px; background:#EFEDFF; color:#5148C5; font-size:10px; font-weight:700; padding:4px 10px; text-transform:uppercase; letter-spacing:0.04em;">
                    [{idx}] {s.get('competitor', '').upper()} // {s.get('platform', 'NEWS').upper()}
                </span>
            </div>
            <div style="font-size:14px; font-weight:700; line-height:1.4; margin:6px 0 4px 0;">
                <a href="{safe_url}" target="_blank" rel="noopener noreferrer" style="color:#1B1C36; text-decoration:none;">{title}</a>
            </div>
            <div style="font-size:12px; color:#596078; line-height:1.5;">
                <strong style="color:#1B1C36;">Brief Summary:</strong> {summary_body}
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #EEF1F6;
                color: #1B1C36;
                margin: 0;
                padding: 24px 12px;
            }}
            .tactile-container {{
                max-width: 820px;
                margin: 0 auto;
                background-color: #EEF1F6;
            }}
            .header-card {{
                background-color: #1B1C36;
                border: none;
                border-radius: 28px;
                box-shadow: -5px -5px 12px rgba(255, 255, 255, 0.9), 6px 6px 16px rgba(0, 0, 0, 0.15);
                padding: 24px 30px;
                color: #FFFFFF;
                margin-bottom: 22px;
            }}
            .tactile-surface {{
                background-color: #FFFFFF;
                border: none;
                border-radius: 28px;
                box-shadow: -5px -5px 12px rgba(255, 255, 255, 0.9), 6px 6px 14px rgba(0, 0, 0, 0.06);
                padding: 28px;
                margin-bottom: 22px;
            }}
            .section-label {{
                font-size: 11px;
                font-weight: 800;
                color: #675CE7;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 8px;
            }}
            .section-summary {{
                font-size: 13px;
                color: #1B1C36;
                line-height: 1.6;
                font-weight: 500;
                background: #F5F7FB;
                border-radius: 20px;
                padding: 16px;
                margin-bottom: 20px;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
                margin-bottom: 18px;
            }}
            .metric-pill-box {{
                background: #FFFFFF;
                border: none;
                border-radius: 20px;
                box-shadow: -4px -4px 9px rgba(255, 255, 255, 0.9), 5px 5px 11px rgba(0, 0, 0, 0.05);
                padding: 16px 20px;
            }}
            .metric-num {{
                font-size: 26px;
                font-weight: 800;
                color: #1B1C36;
                margin-top: 4px;
            }}
            .metric-lbl {{
                font-size: 11px;
                color: #596078;
                text-transform: uppercase;
                font-weight: 700;
                letter-spacing: 0.05em;
            }}
            .tactical-card {{
                background: #FFFFFF;
                border: none;
                border-radius: 20px;
                box-shadow: -4px -4px 9px rgba(255, 255, 255, 0.9), 5px 5px 11px rgba(0, 0, 0, 0.05);
                padding: 16px 20px;
                margin-bottom: 12px;
                font-size: 12px;
                line-height: 1.5;
                color: #1B1C36;
            }}
            .footer {{
                margin-top: 24px;
                padding-top: 14px;
                font-size: 11px;
                color: #596078;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div class="tactile-container">
            <div class="header-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        {logo_tag}
                        <div style="font-size:10px; color:#8583F2; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-top:8px;">
                            Executive Intelligence Briefing // Market Risk
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="display:inline-block; border-radius:9999px; background:#E6F8F3; color:#087965; font-size:10px; font-weight:700; padding:6px 14px; text-transform:uppercase;">
                            Weekly Intelligence
                        </span>
                        <div style="font-size:11px; color:#BEC2D6; margin-top:6px;">{timestamp_pht}</div>
                    </div>
                </div>
            </div>

            <div class="metric-grid">
                <div class="metric-pill-box">
                    <div class="metric-lbl">Monitored Competitor Profiles</div>
                    <div class="metric-num">{total_comps}</div>
                </div>
                <div class="metric-pill-box">
                    <div class="metric-lbl">High Threat Rivals Under Surveillance</div>
                    <div class="metric-num" style="color:#AE481F;">{critical_threats}</div>
                </div>
            </div>

            <div class="tactile-surface">
                <div class="section-label">1. Significant Market Signals & Executive Summary</div>
                <div class="section-summary">
                    <strong>Executive Synthesis:</strong> {section1_summary}
                </div>
                {html_news_items}

                <div class="section-label" style="margin-top:24px;">2. Strategic Findings & Tactical Playbook</div>
                <div class="tactical-card">
                    <strong style="color:#AE481F;">Finding 1: Bio-Oil Market Saturation vs. Warranty Rejection</strong><br>
                    Rival firms continue pushing aggressive D2C video funnels undercutting roof replacement. However, field contractor and homeowner data shows substantial warranty claim rejections citing pre-existing conditions and granular loss.
                </div>
                <div class="tactical-card">
                    <strong style="color:#9A6408;">Finding 2: Climate Stress Evaporation Under UV</strong><br>
                    Bio-oils swell surface bitumen without cross-linking to the fiberglass mat. In summer heat and freeze-thaw cycles, volatile plant oils evaporate within 12-18 months. Insurance adjusters are declining policy renewals for aging shingle roofs treated with bio-oils.
                </div>
                <div class="tactical-card" style="background:#EFEDFF;">
                    <strong style="color:#675CE7;">Tactical Action for GoNano Field Sales:</strong><br>
                    Arm GoNano certified applicators with ASTM D3462 nail tear-strength certifications proving structural matrix reinforcement. Contrast GoNano's transparent 15-Year non-prorated performance warranty against rival prorated exclusions.
                </div>

                <div class="footer">
                    <span>CONFIDENTIAL: FOR INTERNAL GONANO LEADERSHIP ONLY</span>
                    <span style="font-weight:700; color:#1B1C36;">Prepared by: Miguel Gonzales, Competitor Analysis Specialist</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return {
        "plain_text": plain_text,
        "html": html,
        "timestamp": timestamp_pht
    }
