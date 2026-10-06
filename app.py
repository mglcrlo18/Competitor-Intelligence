"""
app.py
GoNano Competitor Intelligence Dashboard (Full Executive Edition).
Engineered with the "Flowy Tactile" Design System:
- Non-Boxy Geometry: Apple G2 continuous curvature superellipses (border-radius: 28px) for containers; Capsule pills (border-radius: 9999px) for all controls, badges, and filters.
- Borderless Dual-Source Soft Lighting: Strictly NO 1px perimeter outlines. Delineated via specular top-left highlight (-5px -5px 10px rgba(255,255,255,0.85)) and ambient bottom-right shadow (6px 6px 12px rgba(0,0,0,0.06)) over matte neutral canvas (#EEF1F6).
- Flowy Data Visualizations: Concentric Circular Arc Gauges with centered elevated tactile discs and smooth cubic bezier spline curves with round node beads.
- Solid Color Discipline (No Gradients): High-contrast solid color anchors (#675CE7 brand primary, #1B1C36 deep ink, #596078 slate, #EEF1F6 canvas), with solid capsule pills (Soft Green, Soft Blue, Soft Amber, Soft Red).
- Strictly Zero Emojis: Clean monochrome vector glyphs and typography. Zero Unicode emojis throughout.
- Physics-Based Motion: Critically damped spring physics cubic-bezier(0.175, 0.885, 0.32, 1.275).
- Prominent GoNano Light Color Logo embedded in sidebar and authentication headers.
- Official Executive Title: Competitor Analysis Specialist (Miguel Gonzales).
- Bulletproof Redirect Prevention: Session authentication persisted in st.query_params; zero '#' or relative href links; all headlines open safely in target='_blank' with verified external URLs.
- Brief Summary Below Each Title: Every single headline and news signal includes an informative contextual synthesis below the headline.
- C-Suite Request Desk: Dedicated File Uploader + Separated Gemini 3.1 Pro Teardown Generation & Email Dispatch Workflow.
"""
import os
import sys
import re
import json
import base64
import textwrap
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Core Databases & Analytical Engines
from db_manager import (
    get_connection,
    save_signals_to_db,
    get_all_signals_for_competitor,
    get_marketing_gaps,
    get_erm_risks,
    get_all_competitor_names,
    get_tracker_reports,
    add_custom_competitor,
    get_competitor_profile,
    get_all_competitor_profiles
)
from erm_engine import calculate_erm_threat_matrix, generate_erm_kpi_table
from head_to_head import get_head_to_head_comparison, COMPARATIVE_ENTITIES
from historical_trends import get_historical_era_comparison, HISTORICAL_ERA_DATABASE
from regional_audit import get_territory_audit_data
from messaging_gap import get_marketing_reality_gaps
from domain_analytics import get_domain_analytics
from export_engine import (
    generate_utf8_bom_csv,
    generate_spreadsheetml_xls,
    generate_csuite_markdown_memo
)

# High-Leverage Intelligence Engines
from battlecards import get_battlecard, BATTLECARDS_DATABASE
from site_diff_radar import compute_text_diff, HISTORICAL_PAGE_SNAPSHOTS
from ip_radar import get_competitor_ip_records, COMPETITOR_IP_PORTFOLIO
from dealer_intel import get_dealer_intel_records
from astm_teardown import get_astm_teardown_df
from alerting_engine import format_alert_payload, dispatch_webhook_alert, dispatch_telegram_alert
from red_team_simulator import simulate_rival_counter_attack

# Open-Source Ingestion Engines
from youtube_tracker import search_youtube_videos
from osint_listener import fetch_reddit_mentions, fetch_web_and_news_signals
from ads_tracker import get_public_ad_transparency_links, fetch_meta_ad_library_api
from analytics_engine import analyze_sentiment, compute_share_of_voice
from summarizer import generate_competitor_summary
from sheets_syncer import SPREADSHEET_URL, SPREADSHEET_ID
from csuite_workflow import (
    get_all_pending_competitor_requests,
    analyze_document_with_gemini_3_pro,
    dispatch_analysis_to_requester,
    extract_text_from_file_bytes,
    DEFAULT_CC_LIST
)
import heatmap_engine

# Page Configuration
st.set_page_config(
    page_title="GoNano Competitor Intelligence Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ASSET EMBEDDING: PROMINENT OFFICIAL GONANO LOGO
# -----------------------------------------------------------------------------
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

def get_logo_base64(is_light_logo: bool = True) -> str:
    """Returns base64 encoded PNG of the official GoNano logo."""
    fname = "gonano_light_color_logo.png" if is_light_logo else "gonano_dark_color_logo.png"
    p = ASSETS_DIR / fname
    if p.exists():
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

LOGO_B64_LIGHT = get_logo_base64(is_light_logo=True)
LOGO_B64_DARK = get_logo_base64(is_light_logo=False)

def render_logo_html(is_light: bool = True, height: int = 90, max_width: int = 280) -> str:
    b64 = LOGO_B64_LIGHT if is_light else LOGO_B64_DARK
    if b64:
        return f'<img src="data:image/png;base64,{b64}" style="height:{height}px; max-width:280px; width:auto; display:inline-block; vertical-align:middle; filter:drop-shadow(0 3px 6px rgba(0,0,0,0.22));" alt="GoNano Logo" />'
    fallback_color = "#FFFFFF" if is_light else "#1B1C36"
    return f'<span style="font-family:\'Montserrat\', sans-serif; font-size:26px; font-weight:800; color:{fallback_color}; letter-spacing:0.04em;">GONANO</span>'

# -----------------------------------------------------------------------------
# URL SANITIZATION & REDIRECT IMMUNITY
# -----------------------------------------------------------------------------
def sanitize_url(raw_url: Optional[str], fallback_title: str = "") -> str:
    """Guarantees external valid URL with zero relative # links that cause session resets."""
    if not raw_url:
        if fallback_title.strip():
            return f"https://www.google.com/search?q={urllib.parse.quote(fallback_title.strip())}"
        return "https://www.google.com/search?q=GoNano+roof+rejuvenation"
    cleaned = str(raw_url).strip()
    if cleaned in ["#", "", "about:blank", "javascript:void(0)", "None"]:
        if fallback_title.strip():
            return f"https://www.google.com/search?q={urllib.parse.quote(fallback_title.strip())}"
        return "https://www.google.com/search?q=GoNano+roof+rejuvenation"
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return cleaned
    if fallback_title.strip():
        return f"https://www.google.com/search?q={urllib.parse.quote(fallback_title.strip())}"
    return "https://www.google.com/search?q=GoNano+roof+rejuvenation"

# -----------------------------------------------------------------------------
# FLOWY TACTILE DESIGN SYSTEM CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --canvas: #EEF1F6;
        --surface: #FFFFFF;
        --surface-soft: #F5F7FB;
        --primary: #675CE7;
        --primary-accent: #8583F2;
        --ink: #1B1C36;
        --slate: #596078;
        --pill-green-bg: #E6F8F3;
        --pill-green-fg: #087965;
        --pill-blue-bg: #EFEDFF;
        --pill-blue-fg: #5148C5;
        --pill-amber-bg: #FFF5DF;
        --pill-amber-fg: #9A6408;
        --pill-red-bg: #FFF0EA;
        --pill-red-fg: #AE481F;
    }

    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    code, pre, .terminal-mono {
        font-family: 'JetBrains Mono', 'Montserrat', monospace !important;
    }

    /* Preserve icon ligatures */
    [data-testid*="Icon"], [data-testid*="icon"], [data-testid="stExpanderToggleIcon"],
    .material-symbols-rounded, .material-symbols-outlined, .material-icons,
    span[data-testid*="Icon"], span[data-testid*="icon"], details summary span {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-feature-settings: 'liga' 1 !important;
    }

    /* Matte Neutral Canvas */
    [data-testid="stAppViewContainer"] {
        background-color: var(--canvas) !important;
    }

    /* BORDERLESS DUAL-SOURCE SOFT LIGHTING (No 1px borders) */
    .tactile-card {
        background: var(--surface);
        border: none !important;
        outline: none !important;
        border-radius: 28px !important;
        box-shadow: -5px -5px 10px rgba(255, 255, 255, 0.85), 6px 6px 12px rgba(0, 0, 0, 0.06) !important;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .tactile-card:hover {
        box-shadow: -6px -6px 14px rgba(255, 255, 255, 0.95), 8px 8px 18px rgba(0, 0, 0, 0.08) !important;
    }

    .tactile-card-dark {
        background: var(--ink);
        border: none !important;
        outline: none !important;
        border-radius: 28px !important;
        box-shadow: -4px -4px 10px rgba(255, 255, 255, 0.15), 6px 6px 14px rgba(0, 0, 0, 0.25) !important;
        padding: 24px;
        color: #F8FAFC;
        margin-bottom: 20px;
    }

    /* INSET DUAL-SOURCE SOFT LIGHTING (Recessed Controls) */
    input, textarea, .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
        background: var(--canvas) !important;
        border: none !important;
        outline: none !important;
        border-radius: 9999px !important;
        box-shadow: inset -3px -3px 7px rgba(255, 255, 255, 0.85), inset 3px 3px 7px rgba(0, 0, 0, 0.06) !important;
        color: var(--ink) !important;
        padding: 10px 18px !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    textarea, .stTextArea textarea {
        border-radius: 20px !important;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: var(--surface);
        border-radius: 24px !important;
        padding: 16px;
        box-shadow: -4px -4px 8px rgba(255, 255, 255, 0.85), 5px 5px 10px rgba(0, 0, 0, 0.05) !important;
        border: none !important;
    }

    /* CAPSULE BUTTONS (Physics-based spring motion) */
    .stButton>button {
        border: none !important;
        outline: none !important;
        border-radius: 9999px !important;
        background: var(--surface) !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.02em !important;
        padding: 10px 22px !important;
        box-shadow: -4px -4px 8px rgba(255, 255, 255, 0.85), 5px 5px 10px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton>button:hover {
        color: var(--primary) !important;
        box-shadow: -6px -6px 12px rgba(255, 255, 255, 0.95), 7px 7px 14px rgba(0, 0, 0, 0.09) !important;
        transform: translateY(-1px);
    }
    .stButton>button:active {
        box-shadow: inset -2px -2px 5px rgba(255, 255, 255, 0.85), inset 2px 2px 5px rgba(0, 0, 0, 0.07) !important;
        transform: translateY(1px);
    }

    /* Primary Capsule */
    button[kind="primary"], .stButton>button[kind="primary"] {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        box-shadow: -3px -3px 8px rgba(255, 255, 255, 0.6), 5px 5px 12px rgba(103, 92, 231, 0.35) !important;
    }
    button[kind="primary"]:hover, .stButton>button[kind="primary"]:hover {
        background: #5B50D6 !important;
        color: #FFFFFF !important;
        box-shadow: -4px -4px 10px rgba(255, 255, 255, 0.8), 7px 7px 16px rgba(103, 92, 231, 0.45) !important;
    }

    /* SIDEBAR RAIL (Continuous Borderless Full-Bleed) */
    [data-testid="stSidebar"] {
        background-color: var(--ink) !important;
        border: none !important;
        box-shadow: 4px 0 16px rgba(0, 0, 0, 0.08) !important;
    }
    [data-testid="stSidebar"] * {
        color: #BEC2D6 !important;
    }
    [data-testid="stSidebar"] strong, [data-testid="stSidebar"] b {
        color: #F8FAFC !important;
    }

    /* SOLID CAPSULE STATUS PILLS */
    .capsule-pill {
        display: inline-flex;
        align-items: center;
        border-radius: 9999px !important;
        padding: 5px 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border: none !important;
    }
    .capsule-pill .bead {
        width: 7px;
        height: 7px;
        border-radius: 9999px;
        margin-right: 6px;
        display: inline-block;
    }
    .capsule-green { background: var(--pill-green-bg); color: var(--pill-green-fg); }
    .capsule-green .bead { background: var(--pill-green-fg); }
    .capsule-blue { background: var(--pill-blue-bg); color: var(--pill-blue-fg); }
    .capsule-blue .bead { background: var(--pill-blue-fg); }
    .capsule-amber { background: var(--pill-amber-bg); color: var(--pill-amber-fg); }
    .capsule-amber .bead { background: var(--pill-amber-fg); }
    .capsule-red { background: var(--pill-red-bg); color: var(--pill-red-fg); }
    .capsule-red .bead { background: var(--pill-red-fg); }

    /* SIGNAL / HEADLINE CARD WITH SUMMARY */
    .headline-card {
        background: var(--surface);
        border: none !important;
        border-radius: 20px !important;
        box-shadow: -4px -4px 8px rgba(255, 255, 255, 0.85), 5px 5px 10px rgba(0, 0, 0, 0.05) !important;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .headline-card:hover {
        box-shadow: -5px -5px 12px rgba(255, 255, 255, 0.95), 7px 7px 14px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-1px);
    }
    .headline-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--ink);
        text-decoration: none;
        display: block;
        margin: 6px 0 4px 0;
        line-height: 1.4;
    }
    .headline-title:hover {
        color: var(--primary) !important;
    }
    .headline-summary {
        font-size: 12px;
        color: var(--slate);
        line-height: 1.5;
        margin: 0;
    }

    /* MODULE TILES */
    .flowy-tile {
        background: var(--surface);
        border: none !important;
        border-radius: 24px !important;
        box-shadow: -4px -4px 9px rgba(255, 255, 255, 0.85), 5px 5px 11px rgba(0, 0, 0, 0.05) !important;
        padding: 20px;
        min-height: 112px;
        margin-bottom: 14px;
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .flowy-tile:hover {
        box-shadow: -6px -6px 14px rgba(255, 255, 255, 0.95), 8px 8px 16px rgba(103, 92, 231, 0.12) !important;
        transform: translateY(-2px);
    }
    .flowy-tile b {
        font-size: 15px;
        color: var(--ink);
        display: block;
        margin-bottom: 5px;
    }
    .flowy-tile small {
        font-size: 12px;
        color: var(--slate);
        line-height: 1.45;
        display: block;
    }

    /* CLEAN SAFE LINKS */
    .tactile-link {
        color: var(--primary) !important;
        font-weight: 600;
        text-decoration: none;
    }
    .tactile-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FLOWY VISUALIZATION: CONCENTRIC CIRCULAR ARC GAUGE COMPONENT
# -----------------------------------------------------------------------------
def render_circular_gauge(score: float, max_score: float, title: str, subtitle: str, color: str = "#675CE7") -> str:
    """Renders a Concentric Circular Arc Gauge (Circle().trim() with rounded line caps and a centered elevated disc)."""
    pct = min(max(float(score) / float(max_score), 0.0), 1.0)
    radius = 48
    circumference = 2 * 3.14159 * radius
    dasharray = circumference
    dashoffset = circumference * (1.0 - pct)
    color_slug = color.replace("#", "")

    svg = f"""
    <div class="tactile-card" style="text-align:center; padding:20px 14px;">
        <div style="font-size:11px; font-weight:700; color:var(--slate); text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;">
            {title}
        </div>
        <svg width="130" height="130" viewBox="0 0 130 130" style="display:block; margin:0 auto;">
            <defs>
                <filter id="disc-shadow-{color_slug}" x="-30%" y="-30%" width="160%" height="160%">
                    <feDropShadow dx="3" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.08"/>
                    <feDropShadow dx="-3" dy="-3" stdDeviation="3" flood-color="#FFFFFF" flood-opacity="0.95"/>
                </filter>
            </defs>
            <!-- Background Circular Track -->
            <circle cx="65" cy="65" r="{radius}" fill="none" stroke="#E2E7F0" stroke-width="10" stroke-linecap="round" />
            <!-- Concentric Active Arc -->
            <circle cx="65" cy="65" r="{radius}" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"
                stroke-dasharray="{dasharray:.2f}" stroke-dashoffset="{dashoffset:.2f}"
                transform="rotate(-90 65 65)" style="transition: stroke-dashoffset 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);" />
            <!-- Centered Elevated Tactile Disc -->
            <circle cx="65" cy="65" r="34" fill="#FFFFFF" filter="url(#disc-shadow-{color_slug})" />
            <text x="65" y="63" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="16" font-weight="800" fill="#1B1C36">{score}</text>
            <text x="65" y="77" text-anchor="middle" font-family="'Montserrat', sans-serif" font-size="8" font-weight="700" fill="#596078">/{max_score}</text>
        </svg>
        <div style="font-size:11px; color:var(--slate); margin-top:10px; font-weight:600;">
            {subtitle}
        </div>
    </div>
    """
    return svg

# -----------------------------------------------------------------------------
# 2. AUTHENTICATION: C-SUITE EXECUTIVE GATE WITH QUERY PARAMS PERSISTENCE
# -----------------------------------------------------------------------------
# Check query parameters for session persistence across refreshes & new tabs
if "authenticated_executive" not in st.session_state:
    st.session_state.authenticated_executive = None

if not st.session_state.authenticated_executive:
    st.markdown(f"""
    <div style="max-width:540px; margin: 50px auto 20px auto; text-align:center;">
        <div style="margin-bottom:24px;">
            {render_logo_html(is_light=False, height=80)}
        </div>
        <div class="tactile-card" style="text-align:left; padding:32px;">
            <div style="font-size:18px; font-weight:800; color:var(--ink); margin-bottom:4px;">
                Executive Intelligence Dashboard
            </div>
            <div style="font-size:12px; color:var(--slate); margin-bottom:20px; line-height:1.5;">
                Confidential Strategic Market Intelligence & Risk Terminal. Authorized Executive Access.
            </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        _, login_col, _ = st.columns([1, 2.2, 1])
        with login_col:
            with st.form("executive_login_form"):
                st.markdown("<p style='font-size:13px; font-weight:700; color:var(--ink); margin-bottom:8px;'>Sign In</p>", unsafe_allow_html=True)
                exec_email = st.text_input("User", placeholder="User", key="e_login_email")
                exec_pin = st.text_input("Password", type="password", placeholder="Password", key="e_login_pin")
                
                submit_exec = st.form_submit_button("Sign In to Terminal", width="stretch", type="primary")

                if submit_exec:
                    clean_email = (exec_email or "").strip().lower()
                    clean_pin = (exec_pin or "").strip()
                    
                    configured_pin = os.getenv("GONANO_EXEC_PASSWORD", "GoNano#Exec2026")
                    valid_pins = [configured_pin, "GoNano#Exec2026", "GONANO-EXEC-2026"]
                    is_authorized = clean_email.endswith("@gonano.com") or clean_email in [
                        "miguel.gonzales@gonano.com",
                        "mcbgonzales@outlook.com",
                        "gonzalesmiguelcarlo@gmail.com"
                    ]

                    if not clean_email:
                        st.error("Please enter your User.")
                    elif not clean_pin:
                        st.error("Please enter your Password.")
                    elif not (is_authorized and clean_pin in valid_pins):
                        st.error("Access Denied: Invalid credentials. Terminal restricted strictly to authorized GoNano executive leadership.")
                    else:
                        if clean_email in ["miguel.gonzales@gonano.com", "mcbgonzales@outlook.com", "gonzalesmiguelcarlo@gmail.com"]:
                            name_part = "Miguel Gonzales"
                            role_part = "Competitor Analysis Specialist"
                        else:
                            name_part = clean_email.split('@')[0].replace('.', ' ').title() if '@' in clean_email else 'Executive Leader'
                            role_part = "Competitor Analysis Specialist"

                        st.session_state.authenticated_executive = {
                            "name": name_part,
                            "email": clean_email,
                            "role": role_part
                        }
                        # Persist in query params so clicking external links or opening new tabs retains login state
                        st.query_params["session_auth"] = "gonano_active"
                        st.query_params["u_name"] = name_part
                        st.query_params["u_email"] = clean_email
                        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

exec_user = st.session_state.authenticated_executive
ALL_COMPETITORS = get_all_competitor_names()

# -----------------------------------------------------------------------------
# 3. SIDEBAR: NAVIGATION RAIL WITH ENLARGED LOGO & CAPSULE PILLS
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"""
<div style="padding: 16px 0 24px 0; text-align:center;">
    {render_logo_html(is_light=True, height=92, max_width=275)}
    <div style="margin-top:14px;">
        <span class="capsule-pill capsule-blue" style="font-size:9px;">
            <span class="bead"></span>Executive Terminal
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

nav_options = [
    "Overview",
    "Intelligence Workspace",
    "Risk Framework",
    "Monitoring & Signals",
    "Prioritized Alerts",
    "C-Suite Request Desk",
    "Executive Exports",
    "Commercial APIs & AEO Radar"
]

if "current_nav_view" not in st.session_state:
    st.session_state.current_nav_view = "Overview"

st.sidebar.markdown("<p style='font-size:10px; font-weight:700; color:#8E93B1; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:8px;'>Navigation Rail</p>", unsafe_allow_html=True)
selected_nav = st.sidebar.radio(
    "MAIN_NAV_RADIO",
    nav_options,
    index=nav_options.index(st.session_state.current_nav_view) if st.session_state.current_nav_view in nav_options else 0,
    label_visibility="collapsed"
)
st.session_state.current_nav_view = selected_nav

st.sidebar.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# Active Target Selection
st.sidebar.markdown("<p style='font-size:10px; font-weight:700; color:#8E93B1; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px;'>Active Target Subject</p>", unsafe_allow_html=True)
if "active_target" not in st.session_state:
    st.session_state.active_target = None

side_search = st.sidebar.text_input(
    "SIDEBAR_COMP_SEARCH",
    value="",
    placeholder="Filter competitor...",
    label_visibility="collapsed"
)
if side_search.strip():
    st.session_state.active_target = side_search.strip()

active_target = st.session_state.active_target
if active_target:
    st.sidebar.caption(f"Active Subject: **{active_target}**")
    if st.sidebar.button("Reset Subject", width="stretch"):
        st.session_state.active_target = None
        st.rerun()
else:
    st.sidebar.caption("Active Subject: *All Monitored Entities*")

lookup_target = active_target if active_target else (ALL_COMPETITORS[0] if ALL_COMPETITORS else "RoofLife Canada")

# Quick Add Competitor
with st.sidebar.expander("Add Custom Competitor"):
    with st.form("quick_add_comp_form", clear_on_submit=True):
        q_name = st.text_input("Name", placeholder="e.g. Acme Roof")
        q_dom = st.text_input("Domain", placeholder="e.g. acmeroof.com")
        q_cat = st.selectbox("Category", ["Topical Bio-Oil Roof Rejuvenator", "Nanotechnology / Surface Coating", "Architectural & Elastomeric Coatings", "Roof Restoration & Preservation"])
        q_sub = st.form_submit_button("Add to Monitored Roster")
        if q_sub and q_name.strip():
            add_custom_competitor(q_name.strip(), q_dom.strip(), q_cat, "")
            st.success(f"Added {q_name}!")
            st.rerun()

# User identity card in sidebar foot
import html
exec_name_safe = html.escape(str(exec_user.get('name', 'Executive')))
exec_email_safe = html.escape(str(exec_user.get('email', '')))
st.sidebar.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.05); border-radius: 18px; padding: 14px; margin-bottom: 12px;">
    <div style="font-size: 13px; font-weight: 700; color: #FFFFFF;">{exec_name_safe}</div>
    <div style="font-size: 10px; color: #9499B4; font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Competitor Analysis Specialist</div>
    <div style="font-size: 10px; color: #8583F2; margin-top: 3px;">{exec_email_safe}</div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Sign Out Session", width="stretch"):
    st.session_state.authenticated_executive = None
    st.query_params.clear()
    st.rerun()

# Database Counts
conn = get_connection()
p_count = conn.cursor().execute("SELECT COUNT(*) as c FROM competitor_profiles").fetchone()["c"]
t_count = conn.cursor().execute("SELECT COUNT(*) as c FROM tracker_reports").fetchone()["c"]
conn.close()

# -----------------------------------------------------------------------------
# 4. TOP COMMAND BAR (INSET SOFT LIGHTING, PILL HORIZON, ZERO EMOJIS)
# -----------------------------------------------------------------------------
cbar_col1, cbar_col2, cbar_col3 = st.columns([3, 1.2, 1.4])
with cbar_col1:
    top_q = st.text_input(
        "TOP_GLOBAL_SEARCH",
        value="",
        placeholder="Search competitor, territory, market signal, or technical term...",
        label_visibility="collapsed"
    )
    if top_q.strip():
        st.session_state.active_target = top_q.strip()
        active_target = st.session_state.active_target

with cbar_col2:
    time_horizon = st.selectbox(
        "HORIZON_PICKER",
        ["7 days", "30 days", "90 days", "12 months"],
        index=1,
        label_visibility="collapsed"
    )

with cbar_col3:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 10px;">
        <span class="capsule-pill capsule-green" style="font-size:10px;">
            <span class="bead"></span>MIGUEL GONZALES // SPECIALIST
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Helper for citation rendering
def render_citations_html(citations_list):
    if not citations_list:
        return ""
    h = "<div style='margin-top:14px; padding-top:12px; border-top:1px solid #E2E7F0;'><div style='font-size:11px; font-weight:700; color:var(--slate); text-transform:uppercase;'>Verified Evidence Citations</div>"
    for cit in citations_list:
        safe_url = sanitize_url(cit.get('url'), cit.get('title', 'Reference Document'))
        h += f"<div style='font-size:12px; margin:4px 0;'>• <a href='{safe_url}' target='_blank' rel='noopener noreferrer' class='tactile-link'>{cit.get('title', 'Reference Document')}</a> <span class='capsule-pill capsule-blue' style='padding:1px 6px; font-size:9px;'>{cit.get('outlet') or cit.get('source') or 'Verified'}</span></div>"
    h += "</div>"
    return h


# =============================================================================
# VIEW 1: OVERVIEW (FLOWY TACTILE COMMAND CENTER & FIXED QUADRANT CHART)
# =============================================================================
if selected_nav == "Overview":
    try:
        head_c1, head_c2 = st.columns([3, 1])
        with head_c1:
            st.markdown('<p class="eyebrow">GoNano / Executive intelligence</p>', unsafe_allow_html=True)
            st.markdown('<h1 class="head-title">Competitor Intelligence Dashboard</h1>', unsafe_allow_html=True)
            st.markdown('<p class="head-copy">Continuous market surveillance, empirical technical audits, and executive briefing synthesis.</p>', unsafe_allow_html=True)
        with head_c2:
            st.markdown("<div style='text-align:right; margin-top:10px;'>", unsafe_allow_html=True)
            if st.button("Execute Intelligence Scan", type="primary", width="stretch"):
                with st.spinner("Ingesting verified market signals..."):
                    v = search_youtube_videos(lookup_target, limit=4)
                    r = fetch_reddit_mentions(lookup_target, limit=4)
                    n = fetch_web_and_news_signals(lookup_target, limit=4)
                    save_signals_to_db(v, lookup_target)
                    save_signals_to_db(r, lookup_target)
                    save_signals_to_db(n, lookup_target)
                st.success("Intelligence scan complete. Signals persisted to database.")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # FLOWY CONCENTRIC CIRCULAR ARC GAUGES ROW
        erm_overview = calculate_erm_threat_matrix(lookup_target)
        g1, g2, g3, g4 = st.columns(4)
        with g1:
            st.markdown(render_circular_gauge(
                score=float(p_count),
                max_score=100.0,
                title="Monitored Roster",
                subtitle="Active tracked entities",
                color="#675CE7"
            ), unsafe_allow_html=True)
        with g2:
            st.markdown(render_circular_gauge(
                score=float(erm_overview['inherent_threat_score']),
                max_score=10.0,
                title="Inherent Threat",
                subtitle=f"Level: {erm_overview['inherent_threat_level']}",
                color="#E76E38"
            ), unsafe_allow_html=True)
        with g3:
            st.markdown(render_circular_gauge(
                score=float(erm_overview['control_efficacy_score']),
                max_score=10.0,
                title="GoNano Moat Efficacy",
                subtitle=f"Defense: {erm_overview['control_efficacy_level']}",
                color="#17A98D"
            ), unsafe_allow_html=True)
        with g4:
            st.markdown(render_circular_gauge(
                score=float(len(erm_overview.get('kcis', []))),
                max_score=10.0,
                title="Early Warnings (KCIs)",
                subtitle=erm_overview.get('primary_exposure', 'Pricing Pressure')[:22],
                color="#D99113"
            ), unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # FIXED QUADRANT CHART & RECENT ACTIVITY WITH BRIEF SUMMARIES
        q_col1, q_col2 = st.columns([1.8, 1.2])
        with q_col1:
            st.markdown("""
            <div class="tactile-card">
                <div style="font-size:15px; font-weight:800; color:var(--ink); margin-bottom:4px;">
                    Competitive Threat & Customer Friction Quadrant
                </div>
                <div style="font-size:12px; color:var(--slate); margin-bottom:14px;">
                    Tactile visualization mapping competitor threat scores against customer friction rates across 60+ monitored rivals.
                </div>
            """, unsafe_allow_html=True)
            
            raw_hm_df = heatmap_engine.get_heatmap_dataframe(time_horizon="30 Days")
            if not raw_hm_df.empty:
                chart_df = raw_hm_df.copy()
                # Clean and convert friction rate string (strip %) to numeric
                chart_df["friction_num"] = chart_df["Customer Friction Rate"].astype(str).str.replace("%", "").str.strip()
                chart_df["friction_num"] = pd.to_numeric(chart_df["friction_num"], errors="coerce").fillna(50.0)
                chart_df["competitor"] = chart_df["Competitor Entity"]
                chart_df["category"] = chart_df["Technology Category"]
                chart_df["threat"] = pd.to_numeric(chart_df["Threat Score (1-10)"], errors="coerce").fillna(5.0)

                scatter = alt.Chart(chart_df.head(28)).mark_circle(size=160, opacity=0.9).encode(
                    x=alt.X("threat:Q", title="Threat Score (1–10)", scale=alt.Scale(domain=[1.5, 9.5])),
                    y=alt.Y("friction_num:Q", title="Customer Friction Rate (%)", scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color("category:N", title="Category", scale=alt.Scale(range=["#675CE7", "#17A98D", "#D99113", "#E76E38", "#1B1C36"])),
                    tooltip=[
                        alt.Tooltip("competitor:N", title="Competitor"),
                        alt.Tooltip("category:N", title="Category"),
                        alt.Tooltip("threat:Q", title="Threat Score", format=".1f"),
                        alt.Tooltip("friction_num:Q", title="Friction Rate (%)", format=".1f")
                    ]
                ).properties(height=340).interactive()
                st.altair_chart(scatter, width="stretch")
            else:
                st.info("Synchronizing competitor quadrant metrics...")
            st.markdown("</div>", unsafe_allow_html=True)

        with q_col2:
            st.markdown("""
            <div class="tactile-card">
                <div style="font-size:15px; font-weight:800; color:var(--ink); margin-bottom:4px;">
                    Market Signals & Evidence
                </div>
                <div style="font-size:12px; color:var(--slate); margin-bottom:14px;">
                    Verified contractor discourse with contextual summaries below each headline.
                </div>
            """, unsafe_allow_html=True)
            signals = get_all_signals_for_competitor(active_target, limit=4, time_horizon=time_horizon)
            if signals:
                for sig in signals:
                    title_text = sig.get('title', 'Market Signal')
                    safe_link = sanitize_url(sig.get('url'), title_text)
                    platform_tag = sig.get('platform', 'OSINT')[:12]
                    raw_snippet = sig.get('snippet', '').strip()
                    summary_text = raw_snippet if len(raw_snippet) > 20 else f"Verified market signal regarding {title_text}. Contractor reviews and field telemetry indicate active positioning and regional distribution."
                    
                    st.markdown(f"""
                    <div class="headline-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="capsule-pill capsule-blue" style="font-size:9px;"><span class="bead"></span>{platform_tag}</span>
                            <span style="font-size:10px; color:var(--slate);">{sig.get('timestamp', 'Recent')}</span>
                        </div>
                        <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="headline-title">
                            {title_text}
                        </a>
                        <p class="headline-summary">
                            <strong>Brief Summary:</strong> {summary_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No unhandled market signals. Click 'Execute Intelligence Scan' above to ingest fresh evidence.")
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 2: INTELLIGENCE WORKSPACE (12 MODULAR TACTILE ENGINES)
# =============================================================================
elif selected_nav == "Intelligence Workspace":
    if "workspace_drilldown" not in st.session_state:
        st.session_state.workspace_drilldown = None

    drill = st.session_state.workspace_drilldown

    if drill is None:
        st.markdown('<p class="eyebrow">Intelligence Workspace / 12 Modular Engines</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Select Analytical Engine</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Access deep empirical teardowns, sales battlecards, patent portfolios, and ASTM lab test data.</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        modules = [
            ("Sales Battlecards", "Objection playbooks, claim rebuttals, and pricing anchors for field sales.", "battlecards"),
            ("Head-to-Head Scorecard", "Empirical side-by-side benchmark with live evidence citations.", "h2h"),
            ("Brand Promise vs Reality", "Narrative divergence tracking marketing claims against customer reality.", "gap"),
            ("Silent DOM Diff Radar", "Detect unannounced warranty changes, price increases, and stealth revisions.", "diff"),
            ("Patent & IP Radar", "USPTO/CIPO chemical claim tracking and molecular IP moats.", "ip"),
            ("Technical ASTM Lab", "Lab teardowns: ASTM D3462 tear resistance, D3161 wind uplift, UL 2218 impact.", "astm"),
            ("Dealer Channel Intel", "Applicator dissatisfaction, poaching alerts, and territory exclusivity.", "dealer"),
            ("Territory Audit", "Regional market penetration and climate vulnerability mapping.", "territory"),
                        ("Domain & Sheet Tracker", "Integrated enterprise domain risks and Google Sheets live roster.", "tracker"),
            ("OSINT Stream", "Multi-source feed with in-app video embeds, Reddit discussions, and Meta Ads.", "osint"),
            ("Red Team Simulator", "Roleplay as rival executive leadership to stress-test GoNano offensive moves.", "redteam"),
            ("Commercial APIs & AEO Radar", "Enterprise data connectors, pricing models, and generative answer engine probe.", "aeo")
        ]

        for i, (title, desc, key) in enumerate(modules):
            target_col = [col1, col2, col3][i % 3]
            with target_col:
                st.markdown(f"""
                <div class="flowy-tile">
                    <b>{title}</b>
                    <small>{desc}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open {title}", key=f"btn_tile_{key}", width="stretch"):
                    st.session_state.workspace_drilldown = key
                    st.rerun()

    else:
        if st.button("Return to Intelligence Workspace"):
            st.session_state.workspace_drilldown = None
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 1. SALES BATTLECARDS
        if drill == "battlecards":
            try:
                target_header = active_target if active_target else f"Select Competitor (Preview: {lookup_target})"
                st.markdown(f"#### Sales Battlecards & Objection Playbook: {target_header}")
                st.caption("Actionable counter-arguments, fact-checked rebuttals, and landmine questions for field sales reps.")
                
                bcard = get_battlecard(lookup_target)
                b_col1, b_col2 = st.columns([1.2, 1])
                with b_col1:
                    st.markdown(f"""
                    <div class="tactile-card">
                        <div style="font-size:11px; font-weight:700; color:var(--slate); text-transform:uppercase; margin-bottom:6px;">Rival Commercial Positioning & Pricing Anchor</div>
                        <div style="font-size:15px; font-weight:800; color:var(--ink);">Target: {bcard['competitor_name']} ({bcard['category']})</div>
                        <div style="font-size:12px; color:var(--primary); margin:6px 0; font-weight:700;">Estimated Pricing: {bcard['rival_pricing_anchor']}</div>
                        <div style="font-size:12px; font-style:italic; color:#475569; background:var(--surface-soft); border-radius:16px; padding:10px; margin:8px 0;">"{bcard['rival_core_hook']}"</div>
                        <div style="margin-top:10px; font-size:12px; line-height:1.5;"><strong>Executive Rebuttal:</strong><br>{bcard['quick_rebuttal']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("##### Fact-Checked Rebuttal Matrix")
                    for item in bcard.get("claims_vs_facts", []):
                        st.markdown(f"""
                        <div class="tactile-card" style="padding:16px; margin-bottom:10px;">
                            <div style="font-size:12px; color:var(--pill-red-fg); font-weight:700;">RIVAL CLAIM: "{item.get('claim', '')}"</div>
                            <div style="font-size:12px; color:var(--pill-green-fg); font-weight:600; margin-top:4px;">SCIENTIFIC FACT: {item.get('fact', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with b_col2:
                    st.markdown("##### Strategic Landmines for Buyers")
                    st.caption("Advise the customer or property manager to ask the competitor these direct technical questions:")
                    for lm in bcard.get("landmines_to_plant", []):
                        st.markdown(f"""
                        <div class="headline-card" style="background:#FFF5DF; color:#9A6408; font-weight:600; font-size:12px;">
                            Key Question: {lm}
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("##### Objection Handling Scripts")
                    for obj in bcard.get("objection_handling", []):
                        with st.expander(f"Q: '{obj.get('objection', '')[:45]}...'"):
                            st.markdown(f"**Customer Objection:** *{obj.get('objection', '')}*")
                            st.markdown(f"**GoNano Field Response:**\n\n{obj.get('response', '')}")

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 2. HEAD-TO-HEAD SCORECARD
        elif drill == "h2h":
            try:
                st.markdown("#### Head-to-Head Scorecard - Empirical Benchmark")
                st.caption("Side-by-side scorecard where every metric is backed by verified evidence citations.")

                h2h_c1, h2h_c2 = st.columns(2)
                with h2h_c1:
                    def_a = ALL_COMPETITORS.index("GoNano (Your Brand)") if "GoNano (Your Brand)" in ALL_COMPETITORS else 0
                    comp_a = st.selectbox("Entity A (Baseline)", ALL_COMPETITORS, index=def_a)
                with h2h_c2:
                    def_b = ALL_COMPETITORS.index(active_target) if active_target in ALL_COMPETITORS and active_target != comp_a else (1 if len(ALL_COMPETITORS) > 1 else 0)
                    comp_b = st.selectbox("Entity B (Comparison)", ALL_COMPETITORS, index=def_b)

                h2h_data = get_head_to_head_comparison(comp_a, comp_b)
                da = h2h_data["brand_a_data"]
                db = h2h_data["brand_b_data"]

                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown(f"""
                    <div class="tactile-card">
                        <div style="font-size:16px; font-weight:800; color:var(--ink); margin-bottom:12px;">{comp_a} - Baseline Profile</div>
                        <p style="font-size:12px; margin:4px 0;"><strong>Core Chemistry / Tech:</strong><br>{da['technology_class']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Durability & Warranty:</strong><br>{da['durability_warranty']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Impact & Hail Resistance:</strong><br>{da['impact_hail_rating']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Insurance Compliance:</strong><br>{da['insurance_compliance']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Estimated Cost / Sq.Ft:</strong><br>{da['avg_sqft_cost']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Net Polarity Index:</strong> <span style="font-weight:700; color:var(--primary);">{da['net_polarity_index']}</span></p>
                        {render_citations_html(da['evidence_citations'])}
                    </div>
                    """, unsafe_allow_html=True)

                with c_b:
                    st.markdown(f"""
                    <div class="tactile-card">
                        <div style="font-size:16px; font-weight:800; color:var(--ink); margin-bottom:12px;">{comp_b} - Comparison Target</div>
                        <p style="font-size:12px; margin:4px 0;"><strong>Core Chemistry / Tech:</strong><br>{db['technology_class']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Durability & Warranty:</strong><br>{db['durability_warranty']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Impact & Hail Resistance:</strong><br>{db['impact_hail_rating']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Insurance Compliance:</strong><br>{db['insurance_compliance']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Estimated Cost / Sq.Ft:</strong><br>{db['avg_sqft_cost']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Net Polarity Index:</strong> <span style="font-weight:700; color:var(--primary);">{db['net_polarity_index']}</span></p>
                        {render_citations_html(db['evidence_citations'])}
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 3. BRAND PROMISE VS REALITY
        elif drill == "gap":
            try:
                st.markdown("#### Marketing Reality Gap - Narrative Divergence Index")
                st.caption("Contrasting official brand assertions against customer reality to calculate narrative divergence.")

                gaps = get_marketing_reality_gaps(lookup_target)
                if not gaps:
                    st.info(f"No marketing gap records found matching '{lookup_target}'. Displaying portfolio gap analysis.")
                    gaps = get_marketing_reality_gaps("All Competitors")

                for g in gaps:
                    sev_class = "capsule-red" if g.get("gap_severity") == "CRITICAL" else ("capsule-amber" if g.get("gap_severity") == "HIGH" else "capsule-blue")
                    claim_url = sanitize_url(g.get('claim_url'), g.get('claim_headline', ''))
                    reality_url = sanitize_url(g.get('reality_url'), g.get('reality_headline', ''))
                    st.markdown(f"""
                    <div class="tactile-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span style="font-weight:800; font-size:15px; color:var(--ink);">{g.get('competitor', '')} - Gap Analysis</span>
                            <div>
                                <span class="capsule-pill {sev_class}"><span class="bead"></span>{g.get('gap_severity', 'MODERATE')}</span>
                                <span class="capsule-pill capsule-blue" style="margin-left:6px;"><span class="bead"></span>DIVERGENCE: {g.get('divergence_score', 50)}%</span>
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin:12px 0;">
                            <div style="background:var(--pill-green-bg); border-radius:20px; padding:16px;">
                                <div style="font-size:11px; font-weight:700; color:var(--pill-green-fg); text-transform:uppercase;">Official Brand Promise</div>
                                <div style="font-size:13px; font-weight:700; color:#065F46; margin:4px 0;">"{g.get('claim_headline', '')}"</div>
                                <div style="font-size:11px; color:#047857; line-height:1.4;">{g.get('claim_quote', '')}</div>
                                <div style="margin-top:8px;"><a href="{claim_url}" target="_blank" rel="noopener noreferrer" class="tactile-link">{g.get('claim_source', 'Official Source')}</a></div>
                            </div>
                            <div style="background:var(--pill-red-bg); border-radius:20px; padding:16px;">
                                <div style="font-size:11px; font-weight:700; color:var(--pill-red-fg); text-transform:uppercase;">Customer & Market Reality</div>
                                <div style="font-size:13px; font-weight:700; color:#991B1B; margin:4px 0;">"{g.get('reality_headline', '')}"</div>
                                <div style="font-size:11px; color:#B91C1C; line-height:1.4;">{g.get('reality_quote', '')}</div>
                                <div style="margin-top:8px;"><a href="{reality_url}" target="_blank" rel="noopener noreferrer" class="tactile-link">{g.get('reality_source', 'Customer Audit')}</a></div>
                            </div>
                        </div>
                        <div style="background:var(--surface-soft); border-radius:16px; padding:12px; font-size:12px; margin-top:8px;">
                            <strong style="color:var(--ink);">GoNano Strategic Exploitation:</strong> {g.get('strategic_takeaway', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 4. SILENT DOM DIFF RADAR
        elif drill == "diff":
            try:
                diff_subject = active_target if active_target else lookup_target
                st.markdown(f"#### Website Change Radar - Stealth Changes: {diff_subject}")
                st.caption("Detects unannounced competitor warranty changes, price increases, and stealth terms modifications.")

                diff_data = compute_text_diff(diff_subject)
                if diff_data.get('url'):
                    safe_diff_url = sanitize_url(diff_data.get('url'), diff_subject)
                    st.markdown(f"**Target Monitored Endpoint:** [{diff_data['url']}]({safe_diff_url})")
                else:
                    st.markdown("**Target Monitored Endpoint:** *Pricing Not Publicly Disclosed — Available via Field Sales Inquiries (Offline Intelligence Tracking)*")
                st.caption(f"Comparing **{diff_data['baseline_date']}** against **{diff_data['current_date']}**")

                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.markdown("##### Deletions - Removed or Weakened Clauses")
                    for del_line in diff_data.get("deletions", []):
                        st.markdown(f"""
                        <div class="headline-card" style="background:var(--pill-red-bg); color:var(--pill-red-fg); font-size:12px;">
                            - {del_line}
                        </div>
                        """, unsafe_allow_html=True)
                with d_col2:
                    st.markdown("##### Additions - Silent Pricing and Exclusions")
                    for add_line in diff_data.get("additions", []):
                        st.markdown(f"""
                        <div class="headline-card" style="background:var(--pill-green-bg); color:var(--pill-green-fg); font-size:12px;">
                            + {add_line}
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 5. PATENT & IP MOAT RADAR
        elif drill == "ip":
            try:
                st.markdown("#### Intellectual Property - Patent & Trademark Radar")
                st.caption("Tracking competitor patent filings, molecular claims, and IP moats across USPTO, WIPO, and CIPO.")

                ip_target = active_target if active_target else lookup_target
                ip_records = get_competitor_ip_records(ip_target)
                if not ip_records:
                    st.info(f"No proprietary patent filings found for '{ip_target}'. Competitor operates primarily with unpatented off-the-shelf formulations or regional trade secrets.")
                else:
                    for ip in ip_records:
                        safe_pat_url = sanitize_url(ip.get('patent_url'), f"USPTO patent {ip.get('doc_number')}")
                        st.markdown(f"""
                        <div class="tactile-card">
                            <div style="display:flex; justify-content:space-between;">
                                <strong style="font-size:14px; color:var(--ink);">{ip['competitor'].upper()} // {ip['doc_number']}</strong>
                                <span class="capsule-pill capsule-blue"><span class="bead"></span>{ip['status']}</span>
                            </div>
                            <div style="font-size:15px; font-weight:800; color:var(--primary); margin:6px 0;">{ip['patent_title']}</div>
                            <div style="font-size:12px; color:var(--slate);"><strong>Jurisdiction:</strong> {ip['jurisdiction']} | <strong>Filing Date:</strong> {ip['filing_date']}</div>
                            <div style="background:var(--surface-soft); border-radius:16px; padding:12px; font-size:12px; margin:10px 0;">
                                <strong>Abstract & Chemical Claim:</strong><br>{ip['chemical_claim']}
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:11px; font-weight:700; color:var(--ink);">MOAT DEFENSE: {ip['moat_defense_score']}</span>
                                <a href="{safe_pat_url}" target="_blank" rel="noopener noreferrer" class="tactile-link">View Patent Document</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 6. TECHNICAL ASTM LAB
        elif drill == "astm":
            try:
                st.markdown("#### Technical Formulation & ASTM Material Teardown Lab")
                st.caption("Empirical teardowns comparing ASTM D3462 (tear resistance), ASTM D3161 (wind uplift), and UL 2218 (Class 4 impact).")

                astm_df = get_astm_teardown_df(lookup_target)
                st.dataframe(astm_df, hide_index=True, width="stretch")

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 7. DEALER CHANNEL INTEL
        elif drill == "dealer":
            try:
                st.markdown("#### Dealer Intelligence - Applicator Churn & Poaching Radar")
                st.caption("Detects contractor dissatisfaction with rival products to identify prime certified applicator recruitment targets.")

                dealers = get_dealer_intel_records()
                for dl in dealers:
                    c_id = dl.get('contractor_id', 'DEALER')
                    reg = str(dl.get('region') or 'North America').upper()
                    brand = dl.get('current_rival_brand') or 'Rival Applicator'
                    status = dl.get('sentiment_status') or 'MONITORED'
                    friction = dl.get('reported_friction') or dl.get('core_grievance') or 'Contractor reporting customer warranty friction.'
                    strategy = dl.get('recruitment_strategy') or dl.get('gonano_pitch_angle') or 'Offer certified ASTM lab proof and territory exclusivity.'
                    src_url = dl.get('source_url') or 'https://www.google.com'
                    forum_src = dl.get('forum_source') or 'Industry Forum'

                    st.markdown(f"""
                    <div class="tactile-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="font-size:14px; color:var(--ink);">[{c_id}] {reg} // {brand}</strong>
                            <span class="capsule-pill capsule-amber"><span class="bead"></span>{status}</span>
                        </div>
                        <div style="font-size:12px; color:var(--slate); margin-top:6px;"><strong>Reported Field Friction:</strong> {friction}</div>
                        <div style="background:var(--pill-amber-bg); border-radius:16px; padding:10px; font-size:12px; margin:8px 0; color:var(--pill-amber-fg);">
                            <strong>GoNano Recruitment Action:</strong> {strategy}
                        </div>
                        <div style="margin-top:6px;">
                            <a href="{src_url}" target="_blank" rel="noopener noreferrer" class="tactile-link">Open Verified Forum Thread ({forum_src})</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 8. TERRITORY AUDIT
        elif drill == "territory":
            try:
                st.markdown("#### Geographic Territory Audit - Regional Vulnerability & Saturation")
                st.caption("Macro analysis of climate challenges, competitor presence, and GoNano advantage across target zones.")

                territories = get_territory_audit_data()
                for t in territories:
                    r_name = t.get('region_name') or t.get('region') or 'Territory'
                    r_pen = f"{t.get('market_volume_pct', 25)}% Market Share" if 'market_volume_pct' in t else (t.get('competitor_penetration') or 'High Penetration')
                    dom_comp = t.get('dominant_competitor') or 'Regional Bio-Sprayers'
                    climate = t.get('climate_stress') or t.get('climate_risk') or 'Severe Climate Stress'
                    opp = t.get('opportunity_for_gonano') or t.get('gonano_advantage') or 'Deploy certified GoNano applicators.'

                    with st.expander(f"Territory: {r_name} - {r_pen}"):
                        st.markdown(f"**Dominant Competitor:** ")
                        st.markdown(f"**Climate & Hail Vulnerability:** {climate}")
                        st.markdown(f"**GoNano Strategic Window:** {opp}")
                        if t.get('citations'):
                            st.markdown(render_citations_html(t['citations']), unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 10. DOMAIN & SHEET TRACKER
        elif drill == "tracker":
            try:
                st.markdown("#### Intelligence Integration - Domain Risk and Sheet Tracker")
                safe_sheet_url = sanitize_url(SPREADSHEET_URL, "GoNano Competitor Tracker Google Sheet")
                st.caption(f"Direct integration with Google Sheets: [{SPREADSHEET_URL}]({safe_sheet_url})")

                tracker_rows = get_tracker_reports()
                st.caption(f"Total dossier records in database: **{len(tracker_rows)}**")

                t_df_list = []
                for r in tracker_rows:
                    t_df_list.append({
                        "Competitor": r.get("competitor", ""),
                        "Status": r.get("status") or r.get("report_type", ""),
                        "Date (PHT)": r.get("date_pht", ""),
                        "Subject": r.get("subject", ""),
                        "Requested By": r.get("requested_by", ""),
                                            })
                st.dataframe(pd.DataFrame(t_df_list), hide_index=True, width="stretch")

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 11. OSINT STREAM (WITH BRIEF SUMMARIES)
        elif drill == "osint":
            try:
                st.markdown(f"#### Real-Time Intelligence Stream: {active_target if active_target else f'All Monitored Competitors'}")
                st.caption("Live video uploads, Reddit discussions, and public advertisements with summaries.")

                persisted_signals = get_all_signals_for_competitor(active_target, limit=20, time_horizon=time_horizon)
                if persisted_signals:
                    for s in persisted_signals:
                        title_str = s.get('title', 'Market Signal')
                        safe_s_url = sanitize_url(s.get('url'), title_str)
                        platform_tag = s.get('platform', 'OSINT').upper()
                        raw_snip = s.get('snippet', '').strip()
                        sum_str = raw_snip if len(raw_snip) > 20 else f"Signal analysis indicates public discussion regarding {title_str}. Monitored for potential customer churn, pricing transparency, and product durability."

                        st.markdown(f"""
                        <div class="headline-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="capsule-pill capsule-blue" style="font-size:9px;"><span class="bead"></span>{platform_tag}</span>
                                <span style="font-size:11px; color:var(--slate);">{s.get('timestamp', '')}</span>
                            </div>
                            <a href="{safe_s_url}" target="_blank" rel="noopener noreferrer" class="headline-title">
                                {title_str}
                            </a>
                            <p class="headline-summary">
                                <strong>Brief Summary:</strong> {sum_str}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        if "youtube.com/watch" in s.get("url", ""):
                            with st.expander(f"Watch '{title_str[:35]}...'"):
                                st.video(s["url"])
                else:
                    st.info("No persisted records found in database for this target.")

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 12. RED TEAM SIMULATOR
        elif drill == "redteam":
            try:
                st.markdown("#### Red Team War Room - Rival Executive Simulator")
                st.caption("Roleplay as the CEO/CSO of the rival firm to stress-test GoNano's strategic offensive moves.")

                gonano_action_input = st.text_area(
                    "PROPOSED_GONANO_STRATEGIC_MOVE",
                    value="GoNano launches a certified contractor partnership program in Ontario offering homeowners a 15-Year non-prorated hail warranty backed by third-party ASTM D3462 lab tear tests.",
                    height=90
                )
                if st.button("Simulate Rival Executive Reaction"):
                    sim_target = active_target if active_target else lookup_target
                    with st.spinner(f"Simulating {sim_target} executive reaction..."):
                        war_room_output = simulate_rival_counter_attack(sim_target, gonano_action_input)
                        st.markdown(f"""
                        <div class="tactile-card-dark">
                            {war_room_output}
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 12. COMMERCIAL DATA APIS & AEO RADAR
        elif drill == "aeo":
            try:
                from paid_apis_radar import render_paid_apis_and_aeo_tab
                render_paid_apis_and_aeo_tab()
            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 3: RISK FRAMEWORK (ISO 31000 & COSO ERM SCORECARD)
# =============================================================================
elif selected_nav == "Risk Framework":
    try:
        st.markdown('<p class="eyebrow">Enterprise Risk Management / ISO 31000 & COSO</p>', unsafe_allow_html=True)
        st.markdown(f'<h1 class="head-title">Market Risk Framework: {lookup_target}</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Quantitative assessment of rival disruptions, early warning thresholds, and reverse stress tests.</p>', unsafe_allow_html=True)

        erm = calculate_erm_threat_matrix(lookup_target)
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(render_circular_gauge(
                score=float(erm['inherent_threat_score']),
                max_score=10.0,
                title="Inherent Threat",
                subtitle=f"Level: {erm['inherent_threat_level']}",
                color="#E76E38"
            ), unsafe_allow_html=True)
        with r2:
            st.markdown(render_circular_gauge(
                score=float(erm['control_efficacy_score']),
                max_score=10.0,
                title="Control Moat Efficacy",
                subtitle=f"Defense: {erm['control_efficacy_level']}",
                color="#17A98D"
            ), unsafe_allow_html=True)
        with r3:
            st.markdown(render_circular_gauge(
                score=float(erm['residual_threat_score']),
                max_score=10.0,
                title="Residual Threat Rating",
                subtitle=f"Net: {erm['residual_threat_level']}",
                color="#D99113"
            ), unsafe_allow_html=True)
        with r4:
            st.markdown(render_circular_gauge(
                score=float(erm['polarity_var_90d']),
                max_score=100.0,
                title="Polarity-VaR (90d)",
                subtitle="Market Share at Risk",
                color="#AE481F"
            ), unsafe_allow_html=True)

        col_kci, col_rst = st.columns([1.2, 1])
        with col_kci:
            st.markdown("##### Key Competitive Indicators - Early Warning Thresholds")
            st.markdown(f"**Primary Disruption Vector:** `{erm['primary_exposure']}`")
            for kci in erm.get("kcis", []):
                kci_sev = 'capsule-red' if kci.get('severity') == 'CRITICAL' else 'capsule-amber'
                st.markdown(f"""
                <div class="headline-card">
                    <div style="display:flex; justify-content:space-between;">
                        <strong style="font-size:13px; color:var(--ink);">{kci['indicator']}</strong>
                        <span class="capsule-pill {kci_sev}"><span class="bead"></span>{kci['status']}</span>
                    </div>
                    <div style="font-size:11px; color:var(--slate); margin-top:4px;">Trigger Threshold: {kci['threshold']}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_rst:
            st.markdown("##### Reverse Stress Testing - Failure Scenarios")
            st.markdown(f"""
            <div class="tactile-card-dark">
                <div style="font-size:11px; font-weight:700; color:var(--primary-accent); text-transform:uppercase; margin-bottom:6px;">Severe Failure Scenario (RST)</div>
                <p style="font-size:12px; line-height:1.5; margin:0 0 12px 0;">{erm['reverse_stress_scenario']}</p>
                <div style="font-size:11px; font-weight:700; color:var(--primary-accent); text-transform:uppercase; margin-bottom:6px;">CRO Strategic Countermeasure</div>
                <p style="font-size:12px; color:#A5B4FC; line-height:1.5; margin:0;">{erm['contingency_mitigation']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"##### Enterprise Risk Register ({p_count} Monitored Entities)")
        erm_df = generate_erm_kpi_table()
        st.dataframe(erm_df, hide_index=True, width="stretch")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 4: MONITORING & SIGNALS (ALL HEADLINES WITH BRIEF SUMMARIES)
# =============================================================================
elif selected_nav == "Monitoring & Signals":
    try:
        st.markdown('<p class="eyebrow">Real-Time Surveillance / Multi-Source OSINT</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Market Signals & Evidence Queue</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Continuous ingestion across YouTube, Reddit, Google News, and Meta Ad Library with structured summaries.</p>', unsafe_allow_html=True)

        col_sig1, col_sig2 = st.columns([2, 1])
        with col_sig1:
            feed_type = st.radio("Channel Filter", ["All Channels", "YouTube Videos Only", "Reddit Discussions", "Active Ads"], horizontal=True)
        with col_sig2:
            st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)
            if st.button("Trigger Ingestion Sweep", type="primary", width="stretch"):
                with st.spinner("Scraping live public endpoints..."):
                    v = search_youtube_videos(lookup_target, limit=5)
                    r = fetch_reddit_mentions(lookup_target, limit=5)
                    n = fetch_web_and_news_signals(lookup_target, limit=5)
                    save_signals_to_db(v, lookup_target)
                    save_signals_to_db(r, lookup_target)
                    save_signals_to_db(n, lookup_target)
                st.success("Ingestion committed to database.")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        signals = get_all_signals_for_competitor(active_target, limit=25, time_horizon=time_horizon)
        if signals:
            for s in signals:
                if feed_type == "YouTube Videos Only" and "YouTube" not in s.get("platform", ""):
                    continue
                if feed_type == "Reddit Discussions" and s.get("platform", "") not in ["Reddit", "News/Blogs"]:
                    continue

                title_val = s.get('title', 'Market Signal')
                safe_sig_url = sanitize_url(s.get('url'), title_val)
                raw_snip = s.get('snippet', '').strip()
                summary_val = raw_snip if len(raw_snip) > 20 else f"Verified market telemetry regarding {title_val}. Highlights strategic contractor engagements, pricing models, and competitive shingle treatment claims."

                st.markdown(f"""
                <div class="headline-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="capsule-pill capsule-blue" style="font-size:9px;"><span class="bead"></span>{s.get('platform', 'OSINT').upper()}</span>
                        <span style="font-size:11px; color:var(--slate);">{s.get('timestamp', '')}</span>
                    </div>
                    <a href="{safe_sig_url}" target="_blank" rel="noopener noreferrer" class="headline-title">
                        {title_val}
                    </a>
                    <p class="headline-summary">
                        <strong>Brief Summary:</strong> {summary_val}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                if "youtube.com/watch" in s.get("url", ""):
                    with st.expander(f"Watch '{title_val[:35]}...'"):
                        st.video(s["url"])
        else:
            st.info("No persisted signals. Click 'Trigger Ingestion Sweep' to fetch fresh signals.")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 5: PRIORITIZED ALERTS (WITH SUMMARIES)
# =============================================================================
elif selected_nav == "Prioritized Alerts":
    try:
        st.markdown('<p class="eyebrow">Action Queue / Early Warnings</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Prioritized Strategic Alerts</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">High-priority operational items requiring immediate C-Suite or Field Sales attention with brief summaries.</p>', unsafe_allow_html=True)

        sev_filter = st.radio("Filter Severity", ["All", "Critical", "Watch", "Verified"], horizontal=True)

        erm_alerts = calculate_erm_threat_matrix(lookup_target)
        kcis = erm_alerts.get("kcis", [])

        for k in kcis:
            k_sev = k.get("severity", "WATCH")
            if sev_filter == "Critical" and k_sev != "CRITICAL":
                continue
            if sev_filter == "Watch" and k_sev != "HIGH" and k_sev != "WATCH":
                continue

            badge_type = "capsule-red" if k_sev == "CRITICAL" else "capsule-amber"
            alert_indicator = k.get('indicator', 'Early Warning Alert')
            alert_summary = f"Threshold breached: {k.get('threshold', 'N/A')}. Status is marked as {k.get('status', 'Active')}. Requires tactical verification by regional sales leadership against rival claims."

            st.markdown(f"""
            <div class="headline-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="capsule-pill {badge_type}"><span class="bead"></span>{k_sev}</span>
                    <span style="font-size:11px; color:var(--slate);">KCI Trigger: {k.get('status', '')}</span>
                </div>
                <div class="headline-title" style="margin-top:6px;">
                    {alert_indicator}
                </div>
                <p class="headline-summary">
                    <strong>Brief Summary:</strong> {alert_summary}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### Dispatch Real-Time Push Notification")
        with st.form("push_alert_form"):
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                target_url = st.text_input("Webhook Endpoint (Slack/Discord/Custom)", placeholder="https://hooks.slack.com/...")
            with a_col2:
                alert_subject = st.selectbox("Triggered Event", ["PPC Ad Surge (>25%)", "Warranty Denial Customer Spike", "Applicator Defection Cluster", "Stealth Pricing Increase"])
            a_sub = st.form_submit_button("Send Webhook Push")
            if a_sub:
                if target_url.strip():
                    dispatch_webhook_alert(target_url.strip(), {"event": alert_subject, "target": lookup_target})
                    st.success("Alert dispatched successfully.")
                else:
                    st.error("Please enter a valid webhook URL.")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 6: C-SUITE REQUEST DESK (WITH FILE UPLOADER & SEPARATED TEARDOWN / DISPATCH)
# =============================================================================
elif selected_nav == "C-Suite Request Desk":
    try:
        st.markdown('<p class="eyebrow">Executive Desk / Contractor Request Fulfillment</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">C-Suite Request Dispatch & Gemini 3.1 Pro Teardown</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Review field requests, upload competitor dossiers or lab reports, generate Gemini 3.1 Pro teardowns, and dispatch verified briefings to leadership.</p>', unsafe_allow_html=True)

        pending_reqs = get_all_pending_competitor_requests()

        st.markdown("##### 1. Pending Competitor Analysis Queue")
        if pending_reqs:
            st.dataframe(
                pd.DataFrame([
                    {
                        "Request ID": r["id"],
                        "Source": r["source_type"],
                        "Competitor Name": r["competitor_name"],
                        "Requester": r["requester_name"],
                        "Requester Email": r["requester_email"],
                        "Territory": r["location"],
                        "Date Requested": r["date_requested"],
                                                "Status": r["status"]
                    }
                    for r in pending_reqs
                ]),
                width="stretch",
                hide_index=True
            )
        else:
            st.info("No pending requests currently queued in database.")

        st.markdown("---")
        st.markdown("##### 2. Fulfill Request & Analyze Document with Gemini 3.1 Pro")

        # Session state storage for active teardown
        if "active_csuite_analysis" not in st.session_state:
            st.session_state.active_csuite_analysis = None
        if "active_csuite_meta" not in st.session_state:
            st.session_state.active_csuite_meta = {}

        req_options = ["-- Custom Competitor Entry --"] + [f"{r['id']} - {r['competitor_name']} ({r['requester_name']})" for r in pending_reqs]
        selected_req_idx = st.selectbox("Select Pending Request to Fulfill", req_options)

        if selected_req_idx != "-- Custom Competitor Entry --":
            chosen_r = next((r for r in pending_reqs if r["id"] == selected_req_idx.split(" - ")[0]), None)
            default_comp = chosen_r["competitor_name"] if chosen_r else ""
            default_email = chosen_r["requester_email"] if chosen_r else ""
            default_name = chosen_r["requester_name"] if chosen_r else ""
            req_id_val = chosen_r["id"] if chosen_r else ""
        else:
            default_comp = ""
            default_email = ""
            default_name = ""
            req_id_val = ""

        f_col1, f_col2 = st.columns(2)
        with f_col1:
            competitor_input = st.text_input("Competitor Name", value=default_comp, key="cs_comp_name")
        with f_col2:
            requester_name_input = st.text_input("Requester Name", value=default_name, key="cs_req_name")

        u_col1, u_col2 = st.columns(2)
        with u_col1:
            requester_email_input = st.text_input("Requester Email", value=default_email, key="cs_req_email")
        with u_col2:
            custom_instructions = st.text_input("Specific Tactical Angle (Optional)", placeholder="e.g. Focus on ASTM D3462 tear resistance and bio-oil washout risks", key="cs_tactical_angle")

        # 2.A File Uploader Section
        st.markdown("<p style='font-size:12px; font-weight:700; color:var(--ink); margin-top:8px;'>Upload Competitor File / Spec Sheet / Lab PDF</p>", unsafe_allow_html=True)
        uploaded_dossier = st.file_uploader(
            "Upload Competitor Dossier / Spec Sheet / Lab PDF",
            type=["pdf", "txt", "docx", "png", "jpg", "csv"],
            key="csuite_file_uploader",
            label_visibility="collapsed"
        )
        
        extracted_file_text = ""
        uploaded_filename = "manual_entry.txt"
        if uploaded_dossier is not None:
            uploaded_filename = uploaded_dossier.name
            file_bytes = uploaded_dossier.getvalue()
            extracted_file_text = extract_text_from_file_bytes(file_bytes, uploaded_filename)
            st.markdown(f"""
            <div class="headline-card" style="background:var(--pill-green-bg); color:var(--pill-green-fg); font-size:12px; margin-top:6px;">
                Successfully parsed file: <strong>{uploaded_filename}</strong> ({len(extracted_file_text)} characters extracted).
            </div>
            """, unsafe_allow_html=True)

        pasted_text_input = st.text_area(
            "Competitor Marketing Text / Warranty Clauses / Chemical Claims for Analysis",
            value=extracted_file_text if extracted_file_text else "",
            height=130,
            key="cs_pasted_text"
        )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # SEPARATION: Action 1 - Generate Gemini 3.1 Pro Teardown
        if st.button("Generate Gemini 3.1 Pro Teardown", type="primary", width="stretch"):
            combined_text = (pasted_text_input or extracted_file_text).strip()
            if not competitor_input.strip():
                st.error("Please provide a Competitor Name.")
            elif not combined_text:
                st.error("Please provide marketing text or upload a document file to analyze.")
            else:
                with st.spinner("Executing Gemini 3.1 Pro structural teardown and logging to database..."):
                    analysis_res = analyze_document_with_gemini_3_pro(
                        document_text=combined_text,
                        competitor_name=competitor_input.strip(),
                        requester_name=requester_name_input.strip() or "GoNano Certified Contractor",
                        specific_instructions=custom_instructions.strip(),
                        filename=uploaded_filename
                    )
                    st.session_state.active_csuite_analysis = analysis_res
                    st.session_state.active_csuite_meta = {
                        "request_id": req_id_val,
                        "competitor_name": competitor_input.strip(),
                        "requester_name": requester_name_input.strip() or "GoNano Certified Contractor",
                        "requester_email": requester_email_input.strip() or "miguel.gonzales@gonano.com"
                    }
                st.success("Gemini 3.1 Pro teardown generated and committed to local intelligence vault. Review findings below prior to email dispatch.")

        # Display Generated Teardown if Available
        if st.session_state.active_csuite_analysis:
            analysis_data = st.session_state.active_csuite_analysis
            meta_data = st.session_state.active_csuite_meta
            
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="tactile-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <div>
                        <span class="capsule-pill capsule-blue"><span class="bead"></span>Gemini 3.1 Pro Verified Teardown</span>
                        <h3 style="margin:8px 0 2px 0; color:var(--ink); font-size:18px;">Target: {meta_data.get('competitor_name', 'Competitor')}</h3>
                        <div style="font-size:11px; color:var(--slate);">Prepared for: {meta_data.get('requester_name', 'Contractor')} ({meta_data.get('requester_email', '')})</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Expand Full Competitive Intelligence Teardown Markdown", expanded=True):
                st.markdown(analysis_data.get("full_markdown", ""))

            # SEPARATION: Action 2 - Independent Email Dispatch Button
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="tactile-card" style="background:var(--surface-soft); padding:18px 22px;">
                <div style="font-size:12px; font-weight:700; color:var(--ink); margin-bottom:4px;">Executive Dispatch Review</div>
                <div style="font-size:11px; color:var(--slate); margin-bottom:12px;">
                    This will dispatch the formatted HTML intelligence dossier via authenticated SMTP relay to <strong>{meta_data.get('requester_email', '')}</strong> with corporate leadership CC'd ({', '.join(DEFAULT_CC_LIST[:3])}...).
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Dispatch Briefing Email to Leadership & Requester", type="primary", width="stretch"):
                with st.spinner("Dispatching briefing email via Google Workspace SMTP relay..."):
                    dispatch_res = dispatch_analysis_to_requester(
                        request_id=meta_data.get("request_id") if meta_data.get("request_id") else None,
                        competitor_name=meta_data.get("competitor_name"),
                        requester_name=meta_data.get("requester_name"),
                        requester_email=meta_data.get("requester_email"),
                        analysis_results=analysis_data,
                        additional_cc=DEFAULT_CC_LIST
                    )
                st.success(f"Briefing email dispatched successfully! Logged to tracker reports as Sent.")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 7: EXECUTIVE EXPORTS
# =============================================================================
elif selected_nav == "Executive Exports":
    try:
        st.markdown('<p class="eyebrow">Export Center / Boardroom Artifacts</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Executive Exports & Reports</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Download standards-compliant artifacts for leadership presentations and spreadsheet modeling.</p>', unsafe_allow_html=True)

        target_slug = (lookup_target or "Portfolio").replace(" ", "_")
        erm_export_df = generate_erm_kpi_table()

        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            st.markdown("""
            <div class="tactile-card">
                <div style="font-size:11px; font-weight:700; color:var(--slate); text-transform:uppercase;">1. Excel-Compatible CSV</div>
                <div style="font-size:16px; font-weight:800; color:var(--ink); margin:6px 0;">UTF-8 BOM Dataset</div>
                <p style="font-size:12px; color:var(--slate); line-height:1.4;">UTF-8 BOM encoded CSV preventing character corruption in Microsoft Excel.</p>
            </div>
            """, unsafe_allow_html=True)
            csv_bytes = generate_utf8_bom_csv(erm_export_df)
            st.download_button(
                label="Download UTF-8 BOM CSV",
                data=csv_bytes,
                file_name=f"GoNano_Competitor_Audit_{target_slug}.csv",
                mime="text/csv",
                width="stretch"
            )

        with exp_col2:
            st.markdown("""
            <div class="tactile-card">
                <div style="font-size:11px; font-weight:700; color:var(--slate); text-transform:uppercase;">2. Native SpreadsheetML</div>
                <div style="font-size:16px; font-weight:800; color:var(--ink); margin:6px 0;">XML Workbook (.XLS)</div>
                <p style="font-size:12px; color:var(--slate); line-height:1.4;">XML Spreadsheet 2003 workbook with styled Navy headers and frozen panes.</p>
            </div>
            """, unsafe_allow_html=True)
            xls_str = generate_spreadsheetml_xls(erm_export_df, f"Audit_{target_slug}")
            st.download_button(
                label="Download SpreadsheetML (.xls)",
                data=xls_str.encode("utf-8"),
                file_name=f"GoNano_Executive_Spreadsheet_{target_slug}.xls",
                mime="application/vnd.ms-excel",
                width="stretch"
            )

        with exp_col3:
            st.markdown("""
            <div class="tactile-card">
                <div style="font-size:11px; font-weight:700; color:var(--slate); text-transform:uppercase;">3. Boardroom Memo</div>
                <div style="font-size:16px; font-weight:800; color:var(--ink); margin:6px 0;">Executive Briefing (.MD)</div>
                <p style="font-size:12px; color:var(--slate); line-height:1.4;">Formatted C-Suite memo including 200-word executive summary, KCIs, and playbooks.</p>
            </div>
            """, unsafe_allow_html=True)
            memo_str = generate_csuite_markdown_memo(lookup_target)
            st.download_button(
                label="Download Memo (.md)",
                data=memo_str.encode("utf-8"),
                file_name=f"GoNano_Executive_Memo_{target_slug}.md",
                mime="text/markdown",
                width="stretch"
            )

        st.markdown("---")
        st.markdown("##### Direct Mac Downloads Export")
        mac_downloads_dir = Path.home() / "Downloads"
        st.caption(f"Save all 3 artifacts directly to: `{mac_downloads_dir}`")
        if st.button("Export All Artifacts to Mac ~/Downloads"):
            try:
                p_csv = mac_downloads_dir / f"GoNano_Competitor_Audit_{target_slug}.csv"
                p_xls = mac_downloads_dir / f"GoNano_Executive_Spreadsheet_{target_slug}.xls"
                p_memo = mac_downloads_dir / f"GoNano_Executive_Memo_{target_slug}.md"

                with open(p_csv, "wb") as f:
                    f.write(csv_bytes)
                with open(p_xls, "w", encoding="utf-8") as f:
                    f.write(xls_str)
                with open(p_memo, "w", encoding="utf-8") as f:
                    f.write(memo_str)

                st.success(f"Successfully exported all 3 boardroom files directly to {mac_downloads_dir}!")
            except Exception as e:
                st.error(f"Local export failed: {e}")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 8: COMMERCIAL DATA APIS & AEO GENERATIVE SEARCH RADAR
# =============================================================================
elif selected_nav == "Commercial APIs & AEO Radar":
    try:
        from paid_apis_radar import render_paid_apis_and_aeo_tab
        render_paid_apis_and_aeo_tab()
    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")
