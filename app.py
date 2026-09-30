"""
app.py
GoNano Competitor Intelligence Command Center (Full Executive Edition).
Restructured with the GoNano Command Center Executive Design System:
- Official GoNano Brand Palette: Deep Navy #1B1C36, Primary Violet #675CE7, Accent Violet #8583F2, Canvas #F6F6FB, Slate #596078, Line #DDE0EB, Teal #17A98D, Amber #D99113, Coral #E76E38
- Sidebar Rail Navigation with 4 Primary Sections (Overview, Intelligence Workspace, Risk & Monitoring, Workflow & Exports)
- Top Command Bar with Live Global Search, Time Horizon Selector, and Miguel Gonzales Executive Verification
- Executive Overview: 4-KPI Grid, Altair Competitive Landscape Scatter Quadrant, and Prioritized Signals Stream
- 12 Modular Intelligence Workspace Engines:
    1. Sales Battlecards & Objection Playbooks (battlecards.py)
    2. Head-to-Head Comparative Scorecard (head_to_head.py)
    3. Brand Promise vs Reality Narrative Gap (messaging_gap.py)
    4. Silent Website & Pricing Diff Detector (site_diff_radar.py)
    5. Patent, Trademark & IP Moat Radar (ip_radar.py)
    6. Technical ASTM Lab & Material Teardown (astm_teardown.py)
    7. Dealer Intelligence & Applicator Poaching Radar (dealer_intel.py)
    8. Regional Geographic Territory Audit (regional_audit.py)
    9. Historical Trends & Shingle Chemistry Evolution (historical_trends.py)
    10. Domain Analytics & Google Sheets Live Competitor Tracker (domain_analytics.py, sheets_syncer.py)
    11. Multi-Source OSINT Real-Time Stream (youtube_tracker.py, osint_listener.py, ads_tracker.py)
    12. Competitor Red Team War Room Simulator (red_team_simulator.py)
- Risk Framework: ISO 31000 & COSO ERM Scorecard, Inherent vs Residual Threat, KCIs, Reverse Stress Testing, Risk Register (erm_engine.py)
- Monitoring & Signals: Live Ingestion Scrape, In-App YouTube Player, Meta Ad Library Transparency, Reddit Discussions
- Prioritized Alerts: Severity-Filtered Action Queue (Critical, Watch, Verified) with Webhook/Telegram Dispatcher (alerting_engine.py)
- C-Suite Request Desk: Pending Requests Queue, Document Upload, Gemini 3.1 Pro Teardown, Auto-Tracker Logging, Authenticated SMTP Email Dispatch (csuite_workflow.py)
- Board-Ready Exports: UTF-8 BOM CSV, Native SpreadsheetML XML (.xls), 200-word Boardroom Executive Markdown Memo, Direct Mac ~/Downloads Export (export_engine.py)
- Defensive try/except error boundaries with "Intelligence Module Advisory" fallback cards across all modules.
"""
import os
import sys
import re
import json
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
    DEFAULT_CC_LIST
)
import heatmap_engine

# Page Configuration
st.set_page_config(
    page_title="GoNano Competitor Intelligence Command Center",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. VISUAL IDENTITY: EXECUTIVE COMMAND CENTER (NAVY, VIOLET, CANVAS, SLATE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --navy: #1B1C36;
        --violet: #675CE7;
        --violet-accent: #8583F2;
        --canvas: #F6F6FB;
        --slate: #596078;
        --line: #DDE0EB;
        --teal: #17A98D;
        --amber: #D99113;
        --coral: #E76E38;
        --white: #FFFFFF;
    }

    html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    button, input, select, textarea, .stSelectbox, .stTextInput {
        font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    code, pre, .terminal-mono {
        font-family: 'Montserrat', monospace !important;
    }

    /* Preserve icon ligatures */
    [data-testid*="Icon"], [data-testid*="icon"], [data-testid="stExpanderToggleIcon"],
    .material-symbols-rounded, .material-symbols-outlined, .material-icons,
    span[data-testid*="Icon"], span[data-testid*="icon"], details summary span {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        font-feature-settings: 'liga' 1 !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: var(--canvas) !important;
    }

    /* Zero-radius boxy geometry */
    div, button, input, select, textarea, [data-testid="stMetric"], .stButton>button {
        border-radius: 0px !important;
    }

    /* Sidebar Rail */
    [data-testid="stSidebar"] {
        background-color: var(--navy) !important;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] * {
        color: #BEC2D6 !important;
    }
    [data-testid="stSidebar"] strong, [data-testid="stSidebar"] b {
        color: #F8FAFC !important;
    }

    /* Headings */
    .eyebrow {
        margin: 0 0 6px 0;
        color: var(--violet);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .head-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: var(--navy);
        margin: 0 0 6px 0;
    }
    .head-copy {
        color: var(--slate);
        font-size: 13px;
        line-height: 1.5;
        margin: 0 0 20px 0;
    }

    /* Boxy KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-left: 4px solid var(--violet);
        padding: 16px;
        margin-bottom: 12px;
    }
    .kpi-card.amber { border-left-color: var(--amber); }
    .kpi-card.teal { border-left-color: var(--teal); }
    .kpi-card.coral { border-left-color: var(--coral); }
    .kpi-val {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.05em;
        color: var(--navy);
        margin: 8px 0 2px 0;
    }
    .kpi-lbl {
        font-size: 11px;
        font-weight: 600;
        color: var(--slate);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-sub {
        font-size: 11px;
        color: var(--slate);
    }

    /* Module Tiles */
    .module-tile {
        background: #FFFFFF;
        border: 1px solid var(--line);
        padding: 16px;
        min-height: 110px;
        margin-bottom: 12px;
        transition: all 0.15s ease;
    }
    .module-tile:hover {
        border-color: var(--violet);
        box-shadow: 4px 4px 0px rgba(103, 92, 231, 0.15);
    }
    .module-tile b {
        font-size: 14px;
        color: var(--navy);
        display: block;
        margin-bottom: 4px;
    }
    .module-tile small {
        font-size: 11px;
        color: var(--slate);
        line-height: 1.4;
        display: block;
    }

    /* Terminal Tile */
    .pulso-tile {
        background-color: #FFFFFF;
        border: 1px solid var(--line);
        border-left: 4px solid var(--navy);
        padding: 16px;
        margin-bottom: 16px;
    }
    .pulso-tile-dark {
        background-color: var(--navy);
        border: 1px solid #1E293B;
        border-left: 4px solid var(--violet);
        padding: 16px;
        color: #F8FAFC;
        margin-bottom: 16px;
    }
    .tile-header {
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        font-weight: 700;
        color: var(--slate);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .tile-header-dark {
        font-family: 'Montserrat', sans-serif;
        font-size: 11px;
        font-weight: 700;
        color: var(--violet-accent);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }

    /* Badges */
    .badge-chip {
        display: inline-block;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 3px 8px;
    }
    .badge-critical { color: #AE481F; background: #FFF0EA; border: 1px solid #FDCFC0; }
    .badge-watch { color: #9A6408; background: #FFF5DF; border: 1px solid #FFE4A8; }
    .badge-good { color: #087965; background: #E6F8F3; border: 1px solid #B7EFE0; }
    .badge-neutral { color: #5148C5; background: #EFEDFF; border: 1px solid #D5D0FC; }

    /* Alert Item Box */
    .alert-row {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-left: 4px solid var(--coral);
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .alert-row.watch { border-left-color: var(--amber); }
    .alert-row.good { border-left-color: var(--teal); }

    /* Social Mentions Stream Card */
    .mention-card {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-left: 4px solid var(--navy);
        padding: 14px;
        margin-bottom: 12px;
    }

    /* Clean, Verified Citation Hyperlinks */
    .citation-block {
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid var(--line);
    }
    .citation-item {
        font-size: 12px;
        margin-bottom: 4px;
        line-height: 1.5;
    }
    .citation-link {
        font-weight: 600;
        color: var(--violet) !important;
        text-decoration: none;
    }
    .citation-link:hover {
        text-decoration: underline;
    }
    .citation-tag {
        font-family: 'Montserrat', sans-serif;
        font-size: 10px;
        font-weight: 700;
        color: var(--violet);
        background: #EFEDFF;
        padding: 1px 4px;
        margin-left: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. AUTHENTICATION: C-SUITE EXECUTIVE & CONTRACTOR LOGIN GATE
# -----------------------------------------------------------------------------
if "authenticated_executive" not in st.session_state:
    st.session_state.authenticated_executive = None

if not st.session_state.authenticated_executive:
    st.markdown("""
    <div style="max-width:540px; margin: 40px auto; background:#1B1C36; border:1px solid #1E293B; border-top:5px solid #675CE7; padding:28px; color:#F8FAFC;">
        <div style="font-size:18px; font-weight:800; color:#F8FAFC; margin-bottom:4px;">
            GONANO // EXECUTIVE COMMAND CENTER
        </div>
        <div style="font-size:12px; color:#94A3B8; margin-bottom:16px;">
            Confidential Strategic Intelligence & Market Risk Terminal. Authorized Executive Access.
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.container():
        _, login_col, _ = st.columns([1, 2.2, 1])
        with login_col:
            with st.form("executive_login_form"):
                st.markdown("##### 🔐 Sign In")
                exec_email = st.text_input("User", placeholder="User", key="e_login_email")
                exec_pin = st.text_input("Password", type="password", placeholder="Password", key="e_login_pin")
                
                submit_exec = st.form_submit_button("Sign In to Executive Terminal", use_container_width=True, type="primary")

                if submit_exec:
                    clean_email = (exec_email or "").strip().lower()
                    clean_pin = (exec_pin or "").strip()
                    
                    # Demo Credentials Support
                    is_demo = (clean_email in ["000", "demo", "demo@gonano.com"] and clean_pin in ["d#m0", "000", "demo"])
                    
                    # Executive Authorized Credentials
                    valid_pins = ["GONANO-EXEC-2026", "GoNano#Exec", "GoNano#2026", "gonano-exec-2026", "d#m0"]
                    is_authorized_email = clean_email.endswith("@gonano.com") or clean_email in [
                        "miguel.gonzales@gonano.com",
                        "mcbgonzales@outlook.com",
                        "gonzalesmiguelcarlo@gmail.com"
                    ]

                    if not clean_email:
                        st.error("Please enter your User.")
                    elif not clean_pin:
                        st.error("Please enter your Password.")
                    elif not (is_demo or (is_authorized_email and clean_pin in valid_pins)):
                        st.error("Access Denied: Invalid credentials. Terminal restricted strictly to authorized GoNano executive leadership.")
                    else:
                        if is_demo:
                            name_part = "Demo Executive"
                            role_part = "GoNano Evaluator"
                        elif clean_email in ["miguel.gonzales@gonano.com", "mcbgonzales@outlook.com", "gonzalesmiguelcarlo@gmail.com"]:
                            name_part = "Miguel Gonzales"
                            role_part = "Lead Strategic Intelligence Analyst"
                        else:
                            name_part = clean_email.split('@')[0].replace('.', ' ').title() if '@' in clean_email else 'Executive Leader'
                            role_part = "GoNano Strategic Intelligence / C-Suite"

                        st.session_state.authenticated_executive = {
                            "name": name_part,
                            "email": clean_email,
                            "role": role_part
                        }
                        st.success(f"Welcome back, {name_part}! Command Center unlocked.")
                        st.rerun()

    st.stop()

exec_user = st.session_state.authenticated_executive
ALL_COMPETITORS = get_all_competitor_names()

# -----------------------------------------------------------------------------
# 3. SIDEBAR: NAVIGATION RAIL (GROUPED CATEGORIES)
# -----------------------------------------------------------------------------
st.sidebar.markdown("""
<div style="padding: 0 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 16px;">
    <div style="font-size: 20px; font-weight: 800; letter-spacing: 0.5px; color: #FFFFFF;">GONANO</div>
    <div style="display:inline-block; margin-top:8px; padding:4px 8px; background:rgba(103,92,231,0.18); color:#D6D3FF; border:1px solid rgba(142,135,250,0.35); font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">
        Executive Terminal
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
    "Executive Exports"
]

if "current_nav_view" not in st.session_state:
    st.session_state.current_nav_view = "Overview"

st.sidebar.markdown("<p style='font-size:10px; font-weight:700; color:#8E93B1; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px;'>Navigation</p>", unsafe_allow_html=True)
selected_nav = st.sidebar.radio(
    "MAIN_NAV_RADIO",
    nav_options,
    index=nav_options.index(st.session_state.current_nav_view) if st.session_state.current_nav_view in nav_options else 0,
    label_visibility="collapsed"
)
st.session_state.current_nav_view = selected_nav

st.sidebar.markdown("---")

# Target Competitor Subject
st.sidebar.markdown("<p style='font-size:10px; font-weight:700; color:#8E93B1; text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px;'>Active Competitor Subject</p>", unsafe_allow_html=True)
if "active_target" not in st.session_state:
    st.session_state.active_target = None

side_search = st.sidebar.text_input(
    "SIDEBAR_COMP_SEARCH",
    value="",
    placeholder="Type competitor (e.g. Roof Maxx)...",
    label_visibility="collapsed"
)
if side_search.strip():
    st.session_state.active_target = side_search.strip()

active_target = st.session_state.active_target
if active_target:
    st.sidebar.caption(f"Active Subject: **{active_target}**")
    if st.sidebar.button("Reset Active Subject", use_container_width=True):
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
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-left: 3px solid #675CE7; padding: 10px; margin-bottom: 12px;">
    <div style="font-size: 12px; font-weight: 700; color: #FFFFFF;">{exec_user['name']}</div>
    <div style="font-size: 10px; color: #9499B4;">{exec_user['role']}</div>
    <div style="font-size: 10px; color: #8583F2; margin-top: 2px;">{exec_user['email']}</div>
</div>
<div style="font-size: 9px; color: #7B819E; line-height: 1.4;">
    Restricted executive workspace. Confidential.
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("Log Out", use_container_width=True):
    st.session_state.authenticated_executive = None
    st.rerun()

# Database Counts
conn = get_connection()
p_count = conn.cursor().execute("SELECT COUNT(*) as c FROM competitor_profiles").fetchone()["c"]
t_count = conn.cursor().execute("SELECT COUNT(*) as c FROM tracker_reports").fetchone()["c"]
g_count = conn.cursor().execute("SELECT COUNT(*) as c FROM marketing_gap_records").fetchone()["c"]
conn.close()

# -----------------------------------------------------------------------------
# 4. TOP COMMAND BAR
# -----------------------------------------------------------------------------
cbar_col1, cbar_col2, cbar_col3 = st.columns([3, 1, 1])
with cbar_col1:
    top_q = st.text_input(
        "TOP_GLOBAL_SEARCH",
        value="",
        placeholder="🔍 Search competitor, territory, signal, or warranty language...",
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
    st.markdown("""
    <div style="text-align: right; padding-top: 8px; font-size: 11px; font-weight: 700; color: #1B1C36;">
        MIGUEL GONZALES <span style="display:inline-block; width:6px; height:6px; background:#17A98D; border-radius:50%; margin-left:4px;"></span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# Helper for citation rendering
def render_citations_html(citations_list):
    if not citations_list:
        return ""
    h = "<div class='citation-block'><div class='tile-header'>Underlying Evidence Citations</div>"
    for cit in citations_list:
        h += f"<div class='citation-item'>• <a href='{cit.get('url', '#')}' target='_blank' class='citation-link'>{cit.get('title', 'Reference Document')}</a> <span class='citation-tag'>SOURCE -></span> <span style='font-size:11px; color:#64748B;'>({cit.get('outlet') or cit.get('source') or 'Verified'})</span></div>"
    h += "</div>"
    return h


# =============================================================================
# VIEW 1: OVERVIEW (COMMAND CENTER)
# =============================================================================
if selected_nav == "Overview":
    try:
        head_c1, head_c2 = st.columns([3, 1])
        with head_c1:
            st.markdown('<p class="eyebrow">GoNano / Executive intelligence</p>', unsafe_allow_html=True)
            st.markdown('<h1 class="head-title">Competitor Intelligence Command Center</h1>', unsafe_allow_html=True)
            st.markdown('<p class="head-copy">Monitor market shifts, organize evidence, and brief leadership with confidence.</p>', unsafe_allow_html=True)
        with head_c2:
            st.markdown("<div style='text-align:right; margin-top:16px;'>", unsafe_allow_html=True)
            if st.button("Run Intelligence Scan", type="primary", use_container_width=True):
                with st.spinner("Executing live multi-source OSINT scrape..."):
                    v = search_youtube_videos(lookup_target, limit=4)
                    r = fetch_reddit_mentions(lookup_target, limit=4)
                    n = fetch_web_and_news_signals(lookup_target, limit=4)
                    save_signals_to_db(v, lookup_target)
                    save_signals_to_db(r, lookup_target)
                    save_signals_to_db(n, lookup_target)
                st.success("Intelligence scan complete. Signals persisted to database.")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # 4-KPI Row
        erm_overview = calculate_erm_threat_matrix(lookup_target)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-lbl">Monitored Competitors</div>
                <div class="kpi-val">{p_count}</div>
                <div class="kpi-sub">Across 5 technology categories</div>
            </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="kpi-card coral">
                <div class="kpi-lbl">Inherent Threat Rating</div>
                <div class="kpi-val">{erm_overview['inherent_threat_score']}/10.0</div>
                <div class="kpi-sub">Level: {erm_overview['inherent_threat_level']}</div>
            </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="kpi-card amber">
                <div class="kpi-lbl">Active Early Warnings (KCIs)</div>
                <div class="kpi-val">{len(erm_overview.get('kcis', []))}</div>
                <div class="kpi-sub">Primary: {erm_overview.get('primary_exposure', 'Pricing Pressure')[:24]}</div>
            </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="kpi-card teal">
                <div class="kpi-lbl">Tracked Reports & Inquiries</div>
                <div class="kpi-val">{t_count}</div>
                <div class="kpi-sub">Synced with Google Sheets tracker</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Competitive Landscape Quadrant & Recent Activity
        q_col1, q_col2 = st.columns([1.8, 1.2])
        with q_col1:
            st.markdown("##### Competitive Threat & Friction Quadrant")
            st.caption("2D positioning: Customer Friction Rate vs. Multi-Factor Threat Score (Calculated by heatmap_engine).")
            hm_df = heatmap_engine.get_heatmap_dataframe(time_horizon="30 Days")
            if not hm_df.empty:
                scatter = alt.Chart(hm_df.head(25)).mark_circle(size=140).encode(
                    x=alt.X("Threat Score (1-10):Q", title="Threat Score (1–10)", scale=alt.Scale(domain=[2, 10])),
                    y=alt.Y("Customer Friction Rate:Q", title="Customer Friction Rate (%)", scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color("Category:N", scale=alt.Scale(range=["#675CE7", "#17A98D", "#D99113", "#E76E38", "#1B1C36"])),
                    tooltip=["Competitor:N", "Category:N", "Threat Score (1-10):Q", "Customer Friction Rate:Q", "Quadrant:N"]
                ).properties(height=360).interactive()
                st.altair_chart(scatter, use_container_width=True)
            else:
                st.info("Heatmap records currently synchronizing...")

        with q_col2:
            st.markdown("##### Real-Time Market Signals Stream")
            st.caption("Latest verified contractor discourse and public announcements.")
            signals = get_all_signals_for_competitor(active_target, limit=4)
            if signals:
                for sig in signals:
                    st.markdown(f"""
                    <div class="alert-row">
                        <span class="badge-chip badge-neutral">{sig.get('platform', 'OSINT')[:8]}</span>
                        <div style="flex:1;">
                            <a href="{sig.get('url', '#')}" target="_blank" style="color:#1B1C36; font-weight:700; font-size:12px; text-decoration:none;">
                                {sig.get('title', 'Signal')[:55]}...
                            </a>
                            <div style="font-size:11px; color:#596078; margin-top:2px;">{sig.get('snippet', '')[:85]}...</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No unhandled signals. Click 'Run Intelligence Scan' above to ingest fresh evidence.")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 2: INTELLIGENCE WORKSPACE (12 DRILL-DOWN ENGINES)
# =============================================================================
elif selected_nav == "Intelligence Workspace":
    if "workspace_drilldown" not in st.session_state:
        st.session_state.workspace_drilldown = None

    drill = st.session_state.workspace_drilldown

    if drill is None:
        st.markdown('<p class="eyebrow">Intelligence Workspace / 12 Modular Engines</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Select Analytical Engine</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Access deep empirical teardowns, battlecards, patent portfolios, and technical ASTM lab data.</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        modules = [
            ("Sales Battlecards", "Objection playbooks, claim rebuttals, and pricing anchors for field reps.", "battlecards"),
            ("Head-to-Head Scorecard", "Empirical side-by-side benchmark with live evidence citations.", "h2h"),
            ("Brand Promise vs Reality", "Narrative divergence tracking marketing claims against customer feedback.", "gap"),
            ("Silent DOM Diff Radar", "Detect unannounced warranty changes, price increases, and stealth alterations.", "diff"),
            ("Patent & IP Radar", "USPTO/CIPO chemical claim tracking and molecular IP moats.", "ip"),
            ("Technical ASTM Lab", "Lab teardowns: ASTM D3462 tear resistance, D3161 wind uplift, UL 2218 impact.", "astm"),
            ("Dealer Channel Intel", "Applicator dissatisfaction, poaching alerts, and territory exclusivity.", "dealer"),
            ("Territory Audit", "Regional market penetration and climate vulnerability mapping.", "territory"),
            ("Historical Trends", "Asphalt shingle chemistry evolution from 1900 to present.", "history"),
            ("Domain & Sheet Tracker", "Integrated enterprise domain risks and Google Sheets live roster.", "tracker"),
            ("OSINT Stream", "Multi-source feed with in-app YouTube embeds, Reddit, and Meta Ads.", "osint"),
            ("Red Team Simulator", "Roleplay as the rival CEO to stress-test GoNano offensive moves.", "redteam")
        ]

        for i, (title, desc, key) in enumerate(modules):
            target_col = [col1, col2, col3][i % 3]
            with target_col:
                st.markdown(f"""
                <div class="module-tile">
                    <b>{title}</b>
                    <small>{desc}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open {title}", key=f"btn_tile_{key}", use_container_width=True):
                    st.session_state.workspace_drilldown = key
                    st.rerun()

    else:
        if st.button("← Return to Intelligence Workspace Grid"):
            st.session_state.workspace_drilldown = None
            st.rerun()

        st.markdown("---")

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
                    <div class="pulso-tile">
                        <div class="tile-header">Rival Commercial Positioning & Pricing Anchor</div>
                        <div style="font-size:14px; font-weight:700; color:#1B1C36;">Target: {bcard['competitor_name']} ({bcard['category']})</div>
                        <div style="font-size:12px; color:#675CE7; margin:6px 0; font-weight:600;">Estimated Pricing: {bcard['rival_pricing_anchor']}</div>
                        <div style="font-size:12px; font-style:italic; color:#475569; background:#F8FAFC; border:1px solid #E2E8F0; padding:8px;">"{bcard['rival_core_hook']}"</div>
                        <div style="margin-top:10px; font-size:12px; line-height:1.5;"><strong>Executive Rebuttal:</strong><br>{bcard['quick_rebuttal']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("##### Fact-Checked Rebuttal Matrix")
                    for item in bcard.get("claims_vs_facts", []):
                        st.markdown(f"""
                        <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-left:4px solid #E76E38; padding:12px; margin-bottom:10px;">
                            <div style="font-size:12px; color:#E76E38; font-weight:700;">RIVAL CLAIM: "{item.get('claim', '')}"</div>
                            <div style="font-size:12px; color:#17A98D; font-weight:600; margin-top:4px;">SCIENTIFIC FACT: {item.get('fact', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with b_col2:
                    st.markdown("##### Strategic Landmines for Buyers")
                    st.caption("Advise the customer or property manager to ask the competitor these direct technical questions:")
                    for lm in bcard.get("landmines_to_plant", []):
                        st.markdown(f"""
                        <div style="background:#FFF5DF; border:1px solid #FFE4A8; border-left:4px solid #D99113; padding:10px; margin-bottom:8px; font-size:12px; color:#9A6408; font-weight:600;">
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
                    comp_a = st.selectbox("ENTITY_A (Baseline)", ALL_COMPETITORS, index=def_a)
                with h2h_c2:
                    def_b = ALL_COMPETITORS.index(active_target) if active_target in ALL_COMPETITORS and active_target != comp_a else (1 if len(ALL_COMPETITORS) > 1 else 0)
                    comp_b = st.selectbox("ENTITY_B (Comparison)", ALL_COMPETITORS, index=def_b)

                h2h_data = get_head_to_head_comparison(comp_a, comp_b)
                da = h2h_data["brand_a_data"]
                db = h2h_data["brand_b_data"]

                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown(f"""
                    <div class="pulso-tile">
                        <div style="font-size:15px; font-weight:700; color:#1B1C36; border-bottom:2px solid #1B1C36; padding-bottom:4px; margin-bottom:12px;">{comp_a} - Baseline Profile</div>
                        <p style="font-size:12px; margin:4px 0;"><strong>Core Chemistry / Tech:</strong><br>{da['technology_class']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Durability & Warranty:</strong><br>{da['durability_warranty']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Impact & Hail Resistance:</strong><br>{da['impact_hail_rating']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Insurance Compliance:</strong><br>{da['insurance_compliance']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Estimated Cost / Sq.Ft:</strong><br>{da['avg_sqft_cost']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Net Polarity Index:</strong> <span style="font-weight:700; color:#675CE7;">{da['net_polarity_index']}</span></p>
                        {render_citations_html(da['evidence_citations'])}
                    </div>
                    """, unsafe_allow_html=True)

                with c_b:
                    st.markdown(f"""
                    <div class="pulso-tile">
                        <div style="font-size:15px; font-weight:700; color:#1B1C36; border-bottom:2px solid #1B1C36; padding-bottom:4px; margin-bottom:12px;">{comp_b} - Comparison Target</div>
                        <p style="font-size:12px; margin:4px 0;"><strong>Core Chemistry / Tech:</strong><br>{db['technology_class']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Durability & Warranty:</strong><br>{db['durability_warranty']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Impact & Hail Resistance:</strong><br>{db['impact_hail_rating']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Insurance Compliance:</strong><br>{db['insurance_compliance']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Estimated Cost / Sq.Ft:</strong><br>{db['avg_sqft_cost']}</p>
                        <p style="font-size:12px; margin:4px 0;"><strong>Net Polarity Index:</strong> <span style="font-weight:700; color:#675CE7;">{db['net_polarity_index']}</span></p>
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
                    sev_class = "badge-critical" if g.get("gap_severity") == "CRITICAL" else ("badge-watch" if g.get("gap_severity") == "HIGH" else "badge-neutral")
                    st.markdown(f"""
                    <div class="pulso-tile">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:700; font-size:14px; color:#1B1C36;">{g.get('competitor', '')} - Gap Analysis</span>
                            <div>
                                <span class="badge-chip {sev_class}">SEVERITY: {g.get('gap_severity', 'MODERATE')}</span>
                                <span class="badge-chip badge-neutral">DIVERGENCE: {g.get('divergence_score', 50)}%</span>
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin:12px 0;">
                            <div style="background:#E6F8F3; border:1px solid #B7EFE0; padding:12px;">
                                <div style="font-size:11px; font-weight:700; color:#087965; text-transform:uppercase;">Official Brand Promise</div>
                                <div style="font-size:13px; font-weight:600; color:#065F46; margin:4px 0;">"{g.get('claim_headline', '')}"</div>
                                <div style="font-size:11px; color:#047857; line-height:1.4;">{g.get('claim_quote', '')}</div>
                                <div style="margin-top:6px;"><a href="{g.get('claim_url', '#')}" target="_blank" class="citation-link">{g.get('claim_source', 'Official Source')} <span class="citation-tag">CLAIM_SOURCE -></span></a></div>
                            </div>
                            <div style="background:#FFF0EA; border:1px solid #FDCFC0; padding:12px;">
                                <div style="font-size:11px; font-weight:700; color:#AE481F; text-transform:uppercase;">Customer & Market Reality</div>
                                <div style="font-size:13px; font-weight:600; color:#991B1B; margin:4px 0;">"{g.get('reality_headline', '')}"</div>
                                <div style="font-size:11px; color:#B91C1C; line-height:1.4;">{g.get('reality_quote', '')}</div>
                                <div style="margin-top:6px;"><a href="{g.get('reality_url', '#')}" target="_blank" class="citation-link">{g.get('reality_source', 'Customer Audit')} <span class="citation-tag">EVIDENCE_SOURCE -></span></a></div>
                            </div>
                        </div>
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:10px; font-size:12px;">
                            <strong style="color:#1B1C36;">GONANO STRATEGIC EXPLOITATION:</strong> {g.get('strategic_takeaway', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 4. SILENT DOM DIFF RADAR
        elif drill == "diff":
            try:
                target_diff_title = active_target if active_target else f"Select Competitor (Preview: {lookup_target})"
                st.markdown(f"#### Website Change Radar - Stealth Changes: {target_diff_title}")
                st.caption("Detects unannounced competitor warranty changes, price increases, and stealth terms modifications.")

                diff_data = compute_text_diff(lookup_target)
                st.markdown(f"**Target Monitored Endpoint:** [{diff_data['url']}]({diff_data['url']})")
                st.caption(f"Comparing **{diff_data['baseline_date']}** against **{diff_data['current_date']}**")

                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    st.markdown("##### Deletions - Removed or Weakened Clauses")
                    for del_line in diff_data.get("deletions", []):
                        st.markdown(f"""
                        <div style="background:#FFF0EA; border:1px solid #FDCFC0; border-left:4px solid #E76E38; padding:8px; margin-bottom:6px; font-size:11px; color:#AE481F;">
                            - {del_line}
                        </div>
                        """, unsafe_allow_html=True)
                with d_col2:
                    st.markdown("##### Additions - Silent Pricing and Exclusions")
                    for add_line in diff_data.get("additions", []):
                        st.markdown(f"""
                        <div style="background:#E6F8F3; border:1px solid #B7EFE0; border-left:4px solid #17A98D; padding:8px; margin-bottom:6px; font-size:11px; color:#087965;">
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
                        st.markdown(f"""
                        <div class="pulso-tile">
                            <div style="display:flex; justify-content:space-between;">
                                <strong style="font-size:13px; color:#1B1C36;">{ip['competitor'].upper()} // {ip['doc_number']}</strong>
                                <span class="badge-chip badge-neutral">{ip['status']}</span>
                            </div>
                            <div style="font-size:14px; font-weight:700; color:#675CE7; margin:6px 0;">{ip['patent_title']}</div>
                            <div style="font-size:12px; color:#596078;"><strong>Jurisdiction:</strong> {ip['jurisdiction']} | <strong>Filing Date:</strong> {ip['filing_date']}</div>
                            <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:10px; font-size:12px; margin:8px 0;">
                                <strong>Abstract & Chemical Claim:</strong><br>{ip['chemical_claim']}
                            </div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:11px; font-weight:700; color:#1B1C36;">MOAT DEFENSE: {ip['moat_defense_score']}</span>
                                <a href="{ip['patent_url']}" target="_blank" class="citation-link">VIEW_USPTO_PATENT_DOCUMENT -></a>
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
                st.dataframe(astm_df, hide_index=True, use_container_width=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 7. DEALER CHANNEL INTEL
        elif drill == "dealer":
            try:
                st.markdown("#### Dealer Intelligence - Applicator Churn & Poaching Radar")
                st.caption("Detects contractor dissatisfaction with rival products to identify prime certified applicator recruitment targets.")

                dealers = get_dealer_intel_records()
                for dl in dealers:
                    st.markdown(f"""
                    <div class="pulso-tile">
                        <div style="display:flex; justify-content:space-between;">
                            <strong style="font-size:13px; color:#1B1C36;">[{dl['contractor_id']}] {dl['region'].upper()} // {dl['current_rival_brand']}</strong>
                            <span class="badge-chip badge-watch">{dl['sentiment_status']}</span>
                        </div>
                        <div style="font-size:12px; color:#596078; margin-top:4px;"><strong>Contractor Profile:</strong> {dl['company_name']} ({dl['applicator_volume_sqft']})</div>
                        <div style="background:#FFF5DF; border:1px solid #FFE4A8; padding:8px; font-size:12px; margin:8px 0; color:#9A6408;">
                            <strong>Reported Dissatisfaction:</strong> {dl['core_grievance']}
                        </div>
                        <div style="font-size:12px; color:#17A98D; font-weight:600;">
                            GoNano Pitch Opportunity: {dl['gonano_pitch_angle']}
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
                    with st.expander(f"📍 {t['region']} - Rival Penetration: {t['competitor_penetration']}"):
                        st.markdown(f"**Dominant Competitor:** `{t['dominant_competitor']}`")
                        st.markdown(f"**Climate & Hail Vulnerability:** {t['climate_risk']}")
                        st.markdown(f"**GoNano Strategic Window:** {t['gonano_advantage']}")

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 9. HISTORICAL TRENDS
        elif drill == "history":
            try:
                st.markdown("#### Historical Trend Analysis - 1900 to Present")
                st.caption("Deep historical timeline detailing the chemical evolution of asphalt shingles and roof preservation techniques.")

                eras = get_historical_era_comparison()
                for e in eras:
                    st.markdown(f"""
                    <div class="pulso-tile">
                        <div style="font-size:14px; font-weight:700; color:#1B1C36;">{e['era_title']} ({e['time_period']})</div>
                        <div style="font-size:12px; color:#675CE7; font-weight:600; margin:4px 0;">Dominant Chemical Process: {e['manufacturing_technology']}</div>
                        <p style="font-size:12px; color:#596078; margin:4px 0;">{e['industry_context']}</p>
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:8px; font-size:11px; margin-top:6px;">
                            <strong>Historical Implication for Rejuvenation:</strong> {e['implication_for_rejuvenation']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 10. DOMAIN & SHEET TRACKER
        elif drill == "tracker":
            try:
                st.markdown("#### Intelligence Integration - Domain Risk and Sheet Tracker")
                st.caption(f"Direct integration with Google Sheets: [{SPREADSHEET_URL}]({SPREADSHEET_URL})")

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
                        "Notes": r.get("notes", "")
                    })
                st.dataframe(pd.DataFrame(t_df_list), hide_index=True, use_container_width=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")

        # 11. OSINT STREAM
        elif drill == "osint":
            try:
                st.markdown(f"#### Real-Time Intelligence Stream: {active_target if active_target else f'All Monitored Competitors'}")
                st.caption("Live video uploads, Reddit discussions, and public advertisements.")

                persisted_signals = get_all_signals_for_competitor(active_target, limit=20)
                if persisted_signals:
                    for s in persisted_signals:
                        st.markdown(f"""
                        <div class="mention-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="badge-chip badge-neutral">{s.get('platform', 'OSINT').upper()}</span>
                                <span style="font-size:11px; color:#596078;">{s.get('timestamp', '')}</span>
                            </div>
                            <div style="font-weight:700; font-size:14px; margin:6px 0;"><a href="{s.get('url', '#')}" target="_blank" style="color:#1B1C36; text-decoration:none;">{s.get('title', '')}</a></div>
                            <div style="font-size:12px; color:#596078; line-height:1.4;">{s.get('snippet', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if "youtube.com/watch" in s.get("url", ""):
                            with st.expander(f"Watch '{s.get('title', '')[:35]}...'"):
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
                if st.button("SIMULATE RIVAL EXECUTIVE COUNTER-ATTACK"):
                    sim_target = active_target if active_target else lookup_target
                    with st.spinner(f"Simulating {sim_target} executive reaction..."):
                        war_room_output = simulate_rival_counter_attack(sim_target, gonano_action_input)
                        st.markdown(f"""
                        <div class="pulso-tile-dark">
                            {war_room_output}
                        </div>
                        """, unsafe_allow_html=True)

            except Exception as tab_err:
                st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 3: RISK FRAMEWORK (ISO 31000 & COSO ERM)
# =============================================================================
elif selected_nav == "Risk Framework":
    try:
        st.markdown('<p class="eyebrow">Enterprise Risk Management / ISO 31000 & COSO</p>', unsafe_allow_html=True)
        st.markdown(f'<h1 class="head-title">Market Risk Framework: {lookup_target}</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Quantitative assessment of rival disruptions, early warning thresholds, and reverse stress tests.</p>', unsafe_allow_html=True)

        erm = calculate_erm_threat_matrix(lookup_target)
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(f"""
            <div class="pulso-tile">
                <div class="tile-header">Inherent Competitive Threat</div>
                <div style="font-size:26px; font-weight:700; color:#1B1C36;">{erm['inherent_threat_score']}/10.0</div>
                <span class="badge-chip badge-critical">LEVEL: {erm['inherent_threat_level']}</span>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            st.markdown(f"""
            <div class="pulso-tile">
                <div class="tile-header">GoNano Control Moat Efficacy</div>
                <div style="font-size:26px; font-weight:700; color:#1B1C36;">{erm['control_efficacy_score']}/10.0</div>
                <span class="badge-chip badge-good">DEFENSE: {erm['control_efficacy_level']}</span>
            </div>
            """, unsafe_allow_html=True)
        with r3:
            st.markdown(f"""
            <div class="pulso-tile">
                <div class="tile-header">Residual Threat Rating</div>
                <div style="font-size:26px; font-weight:700; color:#1B1C36;">{erm['residual_threat_score']}/10.0</div>
                <span class="badge-chip badge-watch">NET: {erm['residual_threat_level']}</span>
            </div>
            """, unsafe_allow_html=True)
        with r4:
            st.markdown(f"""
            <div class="pulso-tile">
                <div class="tile-header">Polarity-VaR (90-Day Downside)</div>
                <div style="font-size:26px; font-weight:700; color:#E76E38;">-{erm['polarity_var_90d']}%</div>
                <span class="badge-chip badge-critical">MARKET SHARE AT RISK</span>
            </div>
            """, unsafe_allow_html=True)

        col_kci, col_rst = st.columns([1.2, 1])
        with col_kci:
            st.markdown("##### Key Competitive Indicators - Early Warning Thresholds")
            st.markdown(f"**Primary Disruption Vector:** `{erm['primary_exposure']}`")
            for kci in erm.get("kcis", []):
                kci_sev = 'badge-critical' if kci.get('severity') == 'CRITICAL' else 'badge-watch'
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #DDE0EB; border-left:4px solid #1B1C36; padding:10px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between;">
                        <strong style="font-size:12px; color:#1B1C36;">{kci['indicator']}</strong>
                        <span class="badge-chip {kci_sev}">{kci['status']}</span>
                    </div>
                    <div style="font-size:11px; color:#596078; margin-top:4px;">Trigger Threshold: {kci['threshold']}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_rst:
            st.markdown("##### Reverse Stress Testing - Failure Scenarios")
            st.markdown(f"""
            <div class="pulso-tile-dark">
                <div class="tile-header-dark">Severe Failure Scenario (RST)</div>
                <p style="font-size:12px; line-height:1.5; margin:0 0 10px 0;">{erm['reverse_stress_scenario']}</p>
                <div class="tile-header-dark" style="margin-top:10px;">CRO Strategic Countermeasure</div>
                <p style="font-size:12px; color:#8583F2; line-height:1.5; margin:0;">{erm['contingency_mitigation']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"##### Enterprise Risk Register ({p_count} Monitored Entities)")
        erm_df = generate_erm_kpi_table()
        st.dataframe(erm_df, hide_index=True, use_container_width=True)

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 4: MONITORING & SIGNALS
# =============================================================================
elif selected_nav == "Monitoring & Signals":
    try:
        st.markdown('<p class="eyebrow">Real-Time Surveillance / Multi-Source OSINT</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Market Signals & Evidence Queue</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Continuous ingestion across YouTube, Reddit, Google News, and Meta Ad Library.</p>', unsafe_allow_html=True)

        col_sig1, col_sig2 = st.columns([2, 1])
        with col_sig1:
            feed_type = st.radio("Channel Filter", ["All Channels", "YouTube Videos Only", "Reddit Discussions", "Active Ads"], horizontal=True)
        with col_sig2:
            st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)
            if st.button("Trigger Live Ingestion", type="primary", use_container_width=True):
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

        signals = get_all_signals_for_competitor(active_target, limit=25)
        if signals:
            for s in signals:
                if feed_type == "YouTube Videos Only" and "YouTube" not in s.get("platform", ""):
                    continue
                if feed_type == "Reddit Discussions" and s.get("platform", "") not in ["Reddit", "News/Blogs"]:
                    continue

                st.markdown(f"""
                <div class="mention-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge-chip badge-neutral">{s.get('platform', 'OSINT').upper()}</span>
                        <span style="font-size:11px; color:#596078;">{s.get('timestamp', '')}</span>
                    </div>
                    <div style="font-weight:700; font-size:14px; margin:6px 0;"><a href="{s.get('url', '#')}" target="_blank" style="color:#1B1C36; text-decoration:none;">{s.get('title', '')}</a></div>
                    <div style="font-size:12px; color:#596078; line-height:1.4;">{s.get('snippet', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                if "youtube.com/watch" in s.get("url", ""):
                    with st.expander(f"Watch '{s.get('title', '')[:35]}...'"):
                        st.video(s["url"])
        else:
            st.info("No persisted signals. Click 'Trigger Live Ingestion' to fetch fresh signals.")

    except Exception as tab_err:
        st.error(f"Intelligence Module Advisory: Encountered a non-fatal exception ({type(tab_err).__name__}: {tab_err}). The rest of the terminal remains fully functional.")


# =============================================================================
# VIEW 5: PRIORITIZED ALERTS
# =============================================================================
elif selected_nav == "Prioritized Alerts":
    try:
        st.markdown('<p class="eyebrow">Action Queue / Early Warnings</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Prioritized Strategic Alerts</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">High-priority operational items requiring C-Suite or Field Sales attention.</p>', unsafe_allow_html=True)

        sev_filter = st.radio("Filter Severity", ["All", "Critical", "Watch", "Verified"], horizontal=True)

        erm_alerts = calculate_erm_threat_matrix(lookup_target)
        kcis = erm_alerts.get("kcis", [])

        for k in kcis:
            k_sev = k.get("severity", "WATCH")
            if sev_filter == "Critical" and k_sev != "CRITICAL":
                continue
            if sev_filter == "Watch" and k_sev != "HIGH" and k_sev != "WATCH":
                continue

            badge_type = "badge-critical" if k_sev == "CRITICAL" else "badge-watch"
            st.markdown(f"""
            <div class="alert-row {'watch' if k_sev != 'CRITICAL' else ''}">
                <span class="badge-chip {badge_type}">{k_sev}</span>
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:13px; color:#1B1C36;">{k.get('indicator', 'Early Warning Alert')}</div>
                    <div style="font-size:11px; color:#596078; margin-top:2px;">Threshold Trigger: {k.get('threshold', '')} | Status: {k.get('status', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### Dispatch Real-Time Push Alert")
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
# VIEW 6: C-SUITE REQUEST DESK (GEMINI 3.1 PRO & AUTOMATED DISPATCH)
# =============================================================================
elif selected_nav == "C-Suite Request Desk":
    try:
        st.markdown('<p class="eyebrow">Executive Desk / Contractor Request Fulfillment</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">C-Suite Request Dispatch & Gemini 3.1 Pro Teardown</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Analyze competitor dossiers with Gemini 3.1 Pro, auto-record findings into Google Sheets, and dispatch executive email briefings.</p>', unsafe_allow_html=True)

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
                        "Notes": r["field_notes"][:90] + ("..." if len(r["field_notes"]) > 90 else ""),
                        "Status": r["status"]
                    }
                    for r in pending_reqs
                ]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No pending requests currently queued in database.")

        st.markdown("---")
        st.markdown("##### 2. Fulfill Request & Analyze Document with Gemini 3.1 Pro")

        with st.form("csuite_fulfillment_form"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                req_options = ["-- Custom Competitor Entry --"] + [f"{r['id']} - {r['competitor_name']} ({r['requester_name']})" for r in pending_reqs]
                selected_req_idx = st.selectbox("Select Pending Request", req_options)
            with f_col2:
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

                competitor_input = st.text_input("Competitor Name", value=default_comp)

            u_col1, u_col2 = st.columns(2)
            with u_col1:
                requester_name_input = st.text_input("Requester Name", value=default_name)
            with u_col2:
                requester_email_input = st.text_input("Requester Email", value=default_email)

            pasted_text_input = st.text_area("Competitor Marketing Text / Warranty / Chemical Claim for Analysis", height=120)
            custom_instructions = st.text_input("Specific Tactical Angle (Optional)", placeholder="e.g. Focus on ASTM D3462 tear resistance and bio-oil washout risks")

            submit_analysis = st.form_submit_button("Generate Gemini 3.1 Pro Teardown & Dispatch", type="primary", use_container_width=True)

            if submit_analysis:
                if not competitor_input.strip():
                    st.error("Please provide a competitor name.")
                elif not pasted_text_input.strip():
                    st.error("Please provide marketing or technical text to analyze.")
                else:
                    with st.spinner("Executing Gemini 3.1 Pro teardown, recording to database, and dispatching briefing..."):
                        analysis_res = analyze_document_with_gemini_3_pro(
                            document_text=pasted_text_input.strip(),
                            competitor_name=competitor_input.strip(),
                            requester_name=requester_name_input.strip() or "GoNano Contractor",
                            specific_instructions=custom_instructions.strip()
                        )
                        dispatch_res = dispatch_analysis_to_requester(
                            request_id=req_id_val if req_id_val else None,
                            competitor_name=competitor_input.strip(),
                            requester_name=requester_name_input.strip() or "GoNano Contractor",
                            requester_email=requester_email_input.strip() or "miguel.gonzales@gonano.com",
                            analysis_results=analysis_res,
                            additional_cc=DEFAULT_CC_LIST
                        )

                    st.success("Executive teardown generated, logged into database/tracker, and dispatched via SMTP relay.")
                    with st.expander("View Full Gemini 3.1 Pro Teardown Output", expanded=True):
                        st.markdown(analysis_res.get("full_markdown", ""))

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
            <div class="pulso-tile">
                <div class="tile-header">1. Excel-Compatible CSV</div>
                <p style="font-size:12px; color:#596078;">UTF-8 BOM encoded CSV preventing character corruption in Microsoft Excel.</p>
            </div>
            """, unsafe_allow_html=True)
            csv_bytes = generate_utf8_bom_csv(erm_export_df)
            st.download_button(
                label="Download UTF-8 BOM CSV",
                data=csv_bytes,
                file_name=f"GoNano_Competitor_Audit_{target_slug}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with exp_col2:
            st.markdown("""
            <div class="pulso-tile">
                <div class="tile-header">2. Native SpreadsheetML (.XLS)</div>
                <p style="font-size:12px; color:#596078;">XML Spreadsheet 2003 workbook with styled Navy headers and frozen panes.</p>
            </div>
            """, unsafe_allow_html=True)
            xls_str = generate_spreadsheetml_xls(erm_export_df, f"Audit_{target_slug}")
            st.download_button(
                label="Download SpreadsheetML (.xls)",
                data=xls_str.encode("utf-8"),
                file_name=f"GoNano_Executive_Spreadsheet_{target_slug}.xls",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

        with exp_col3:
            st.markdown("""
            <div class="pulso-tile">
                <div class="tile-header">3. Boardroom Memo (.MD)</div>
                <p style="font-size:12px; color:#596078;">Formatted C-Suite memo including 200-word executive summary, KCIs, and playbooks.</p>
            </div>
            """, unsafe_allow_html=True)
            memo_str = generate_csuite_markdown_memo(lookup_target)
            st.download_button(
                label="Download Memo (.md)",
                data=memo_str.encode("utf-8"),
                file_name=f"GoNano_Executive_Memo_{target_slug}.md",
                mime="text/markdown",
                use_container_width=True
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
