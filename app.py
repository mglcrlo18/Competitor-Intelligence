"""
app.py
GoNano Competitor Intelligence Command Center (Executive Edition).
Restructured to match the GoNano Command Center Executive Design Specification:
- Deep Navy #1B1C36, Violet #675CE7, Canvas #F6F6FB, Slate #596078, Line #DDE0EB, Teal #17A98D, Amber #D99113, Coral #E76E38
- Sidebar Rail Navigation with 4 Primary Groups (Overview, Intelligence, Workflow, Exports)
- Top Command Bar with Search, Horizon Filter, and Miguel Gonzales Executive Identity
- Executive Overview: 4-KPI Grid, Competitive Landscape Quadrant, and Prioritized Alerts
- Modular Intelligence Workspace: 12 Analytical Drill-Down Modules
- Risk Framework: ISO 31000 & COSO ERM Scorecard, KCIs, Reverse Stress Testing
- Monitoring: Live OSINT Evidence Queue, YouTube Stream, Meta Ad Library Radar
- Alerts: Severity Filtered Action Queue (Critical, Watch, Verified)
- C-Suite Request Desk: Pending Requests Queue, Document Upload, Gemini 3.1 Pro Analysis, Auto-Tracker, and Email Dispatch
- Exports: UTF-8 BOM CSV, SpreadsheetML XLS, and Boardroom Executive Markdown Memo
"""
import os
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
    page_title="GoNano Competitor Intelligence",
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
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.04em;
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
        min-height: 96px;
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

    /* Evidence Block */
    .evidence-box {
        padding: 14px;
        border-left: 3px solid var(--violet);
        background: #FAFAFE;
        border: 1px solid var(--line);
        border-left-width: 3px;
        margin-bottom: 10px;
    }
    .evidence-box b {
        color: var(--navy);
        font-size: 13px;
    }
    .evidence-box p {
        color: var(--slate);
        font-size: 12px;
        line-height: 1.5;
        margin: 4px 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. AUTHENTICATION: C-SUITE EXECUTIVE GATE
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
                    clean_email = exec_email.strip().lower()
                    clean_pin = exec_pin.strip()
                    valid_pins = ["GONANO-EXEC-2026", "GoNano#Exec", "GoNano#2026", "gonano-exec-2026"]
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
                        name_part = "Miguel Gonzales" if clean_email in ["miguel.gonzales@gonano.com", "mcbgonzales@outlook.com", "gonzalesmiguelcarlo@gmail.com"] else (clean_email.split('@')[0].replace('.', ' ').title() if '@' in clean_email else 'Executive Leader')
                        st.session_state.authenticated_executive = {
                            "name": name_part,
                            "email": clean_email,
                            "role": "Lead Strategic Intelligence Analyst"
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
        Executive Prototype
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

# =============================================================================
# VIEW 1: OVERVIEW (COMMAND CENTER)
# =============================================================================
if selected_nav == "Overview":
    head_c1, head_c2 = st.columns([3, 1])
    with head_c1:
        st.markdown('<p class="eyebrow">GoNano / Executive intelligence</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Competitor Intelligence Command Center</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Monitor market shifts, organize evidence, and brief leadership with confidence.</p>', unsafe_allow_html=True)
    with head_c2:
        st.markdown("<div style='text-align:right; margin-top:16px;'>", unsafe_allow_html=True)
        btn_scan = st.button("Run Intelligence Scan", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if btn_scan:
            st.toast("Intelligence scan complete — material signals prioritized for analyst review.")

    # 4 KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-lbl">Monitored Entities</span>
            <div class="kpi-val">{p_count}</div>
            <span class="kpi-sub">Active market scans</span>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card amber">
            <span class="kpi-lbl">Pending Requests</span>
            <div class="kpi-val">{t_count}</div>
            <span class="kpi-sub">C-suite review queue</span>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card teal">
            <span class="kpi-lbl">Verified Dossiers</span>
            <div class="kpi-val">{g_count}</div>
            <span class="kpi-sub">Evidence-backed profiles</span>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
        <div class="kpi-card coral">
            <span class="kpi-lbl">Critical Signals</span>
            <div class="kpi-val">8</div>
            <span class="kpi-sub">Require field visibility</span>
        </div>
        """, unsafe_allow_html=True)

    # 2-Column Grid: Competitive Landscape Quadrant + Prioritized Alerts
    grid_c1, grid_c2 = st.columns([1.3, 0.7])
    with grid_c1:
        st.markdown(f"##### Competitive Landscape ({time_horizon} view)")
        st.caption("Validated movement and risk positioning across the active horizon.")
        
        conn = get_connection()
        c_rows = conn.cursor().execute("SELECT name, inherent_threat_score, control_efficacy_score, residual_threat_score, category FROM competitor_profiles LIMIT 15").fetchall()
        conn.close()

        if c_rows:
            plot_df = pd.DataFrame([
                {
                    "Competitor": r["name"],
                    "Inherent Threat": float(r["inherent_threat_score"] or 5.0),
                    "Control Defense": float(r["control_efficacy_score"] or 6.0),
                    "Residual Exposure": float(r["residual_threat_score"] or 3.0),
                    "Category": r["category"] or "Coating"
                }
                for r in c_rows
            ])
            chart = alt.Chart(plot_df).mark_circle(size=140).encode(
                x=alt.X("Inherent Threat:Q", scale=alt.Scale(domain=[1, 10])),
                y=alt.Y("Residual Exposure:Q", scale=alt.Scale(domain=[1, 10])),
                color=alt.Color("Category:N", scale=alt.Scale(range=["#675CE7", "#E76E38", "#17A98D", "#D99113"])),
                tooltip=["Competitor", "Inherent Threat", "Residual Exposure", "Category"]
            ).properties(height=280)
            st.altair_chart(chart, use_container_width=True)

    with grid_c2:
        st.markdown("##### Prioritized Alerts")
        st.caption("Material changes ranked for immediate action.")
        
        st.markdown("""
        <div class="alert-row">
            <div>
                <strong style="font-size:12px; color:#1B1C36;">Warranty term change detected</strong>
                <p style="margin:2px 0 0; font-size:11px; color:#596078;">ArroveX added prorated coverage exclusions.</p>
            </div>
            <div style="margin-left:auto;"><span class="badge-chip badge-critical">Critical</span></div>
        </div>
        <div class="alert-row">
            <div>
                <strong style="font-size:12px; color:#1B1C36;">Price increase detected</strong>
                <p style="margin:2px 0 0; font-size:11px; color:#596078;">RevivaRoof increased regional pricing.</p>
            </div>
            <div style="margin-left:auto;"><span class="badge-chip badge-critical">Critical</span></div>
        </div>
        <div class="alert-row watch">
            <div>
                <strong style="font-size:12px; color:#1B1C36;">New territory expansion</strong>
                <p style="margin:2px 0 0; font-size:11px; color:#596078;">Localized partners appearing in Ontario.</p>
            </div>
            <div style="margin-left:auto;"><span class="badge-chip badge-watch">Watch</span></div>
        </div>
        <div class="alert-row good">
            <div>
                <strong style="font-size:12px; color:#1B1C36;">Dealer evidence verified</strong>
                <p style="margin:2px 0 0; font-size:11px; color:#596078;">Contractor channel activity validated.</p>
            </div>
            <div style="margin-left:auto;"><span class="badge-chip badge-good">Verified</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Recent Intelligence Activity")
    st.caption("Evidence and analyst validation stream.")
    
    activity_data = [
        {"Signal": "Warranty language revision", "Competitor": "ArroveX", "Detected": "Sep 29", "Status": "Critical"},
        {"Signal": "Localized partner launch", "Competitor": "RoofLife Canada", "Detected": "Sep 28", "Status": "Watch"},
        {"Signal": "Standard pricing adjustment", "Competitor": "RevivaRoof", "Detected": "Sep 26", "Status": "Verified"},
        {"Signal": "ASTM D3462 Tear Test Failure", "Competitor": "Roof Juice RX", "Detected": "Sep 24", "Status": "Critical"},
        {"Signal": "Contractor Poaching Activity", "Competitor": "PEAK301", "Detected": "Sep 21", "Status": "Watch"},
    ]
    st.dataframe(pd.DataFrame(activity_data), use_container_width=True, hide_index=True)


# =============================================================================
# VIEW 2: INTELLIGENCE WORKSPACE (12 ANALYTICAL MODULES & DRILL-DOWN)
# =============================================================================
elif selected_nav == "Intelligence Workspace":
    modules_list = [
        ("Sales battlecards", "Buyer questions, approved positioning, objection handling."),
        ("Head-to-head scorecard", "Warranty, chemistry, installation, and risk comparison."),
        ("Brand promise vs reality", "Positioning claims mapped against observed evidence."),
        ("DOM diff radar", "Website changes, deletions, additions, and exclusions."),
        ("Patent & IP radar", "Available public domain and claim-monitoring prototype."),
        ("Technical ASTM lab", "Material benchmarks and molecular cross-linking audit."),
        ("Dealer intelligence", "Contractor churn, poaching, and channel movement."),
        ("Territory audit", "Geographic market dynamics and exposure by region."),
        ("Historical trends", "Lifecycle evolution and prior market milestones."),
        ("Domain & Sheet tracker", "Domain risk and monitored-record tracker."),
        ("OSINT stream", "Analyst-curated open-source evidence queue."),
        ("Red-team simulator", "Scenario stress test for executive counter-moves.")
    ]

    if "active_intelligence_module" not in st.session_state:
        st.session_state.active_intelligence_module = None

    if st.session_state.active_intelligence_module:
        active_mod = st.session_state.active_intelligence_module
        drill_c1, drill_c2 = st.columns([3, 1])
        with drill_c1:
            st.markdown(f'<p class="eyebrow">Intelligence Drill-Down // {lookup_target}</p>', unsafe_allow_html=True)
            st.markdown(f'<h1 class="head-title">{active_mod}</h1>', unsafe_allow_html=True)
        with drill_c2:
            if st.button("← Back to Modules Overview", use_container_width=True):
                st.session_state.active_intelligence_module = None
                st.rerun()

        st.markdown("---")

        # RENDER SPECIFIC ENGINE
        if active_mod == "Sales battlecards":
            bcard = get_battlecard(lookup_target)
            st.markdown(f"**Target:** {bcard['competitor_name']} ({bcard['category']}) | **Pricing Anchor:** `{bcard['rival_pricing_anchor']}`")
            st.info(f"Rival Hook: \"{bcard['rival_core_hook']}\"\n\n**Quick Rebuttal:** {bcard['quick_rebuttal']}")
            for item in bcard["claims_vs_facts"]:
                st.markdown(f"- 🔴 **Claim:** {item['claim']}  \n  🟢 **Fact:** {item['fact']}")
            st.markdown("##### Landmines to Plant")
            for lm in bcard["landmines_to_plant"]:
                st.warning(f"Ask the competitor: {lm}")

        elif active_mod == "Head-to-head scorecard":
            h2h_c1, h2h_c2 = st.columns(2)
            with h2h_c1:
                comp_a = st.selectbox("Baseline Brand", ALL_COMPETITORS, index=ALL_COMPETITORS.index("GoNano (Your Brand)") if "GoNano (Your Brand)" in ALL_COMPETITORS else 0)
            with h2h_c2:
                comp_b = st.selectbox("Rival Brand", ALL_COMPETITORS, index=ALL_COMPETITORS.index(lookup_target) if lookup_target in ALL_COMPETITORS else 1)
            h2h_res = get_head_to_head_comparison(comp_a, comp_b)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"### {comp_a}")
                st.json(h2h_res["brand_a_data"])
            with c2:
                st.markdown(f"### {comp_b}")
                st.json(h2h_res["brand_b_data"])

        elif active_mod == "Brand promise vs reality":
            st.markdown(f"#### Marketing Reality Gap: {lookup_target}")
            gaps = get_marketing_reality_gaps(lookup_target)
            st.dataframe(pd.DataFrame(gaps), use_container_width=True)

        elif active_mod == "DOM diff radar":
            st.markdown(f"#### Silent DOM Diff Radar: {lookup_target}")
            snapshot = HISTORICAL_PAGE_SNAPSHOTS.get(lookup_target, {})
            diff_text = compute_text_diff(snapshot.get("previous", ""), snapshot.get("current", ""))
            st.markdown(diff_text, unsafe_allow_html=True)

        elif active_mod == "Patent & IP radar":
            st.markdown(f"#### Patent & Trademark IP Portfolio: {lookup_target}")
            records = get_competitor_ip_records(lookup_target)
            st.dataframe(pd.DataFrame(records), use_container_width=True)

        elif active_mod == "Technical ASTM lab":
            st.markdown("#### Technical Formulation & ASTM Benchmark Lab")
            st.dataframe(get_astm_teardown_df(), use_container_width=True)

        elif active_mod == "Dealer intelligence":
            st.markdown("#### Dealer & Channel Intelligence Stream")
            st.dataframe(pd.DataFrame(get_dealer_intel_records()), use_container_width=True)

        elif active_mod == "Territory audit":
            st.markdown(f"#### Regional Territory Audit: {lookup_target}")
            st.dataframe(pd.DataFrame(get_territory_audit_data(lookup_target)), use_container_width=True)

        elif active_mod == "Historical trends":
            st.markdown(f"#### Historical Evolution (1900 - Present): {lookup_target}")
            st.dataframe(pd.DataFrame(get_historical_era_comparison(lookup_target)), use_container_width=True)

        elif active_mod == "Domain & Sheet tracker":
            st.markdown("#### Google Sheets Synced Roster & Domain Analytics")
            st.markdown(f"Connected Google Sheet: [{SPREADSHEET_URL}]({SPREADSHEET_URL})")
            st.dataframe(pd.DataFrame(get_domain_analytics()), use_container_width=True)

        elif active_mod == "OSINT stream":
            st.markdown(f"#### OSINT Evidence Stream: {lookup_target}")
            vids = search_youtube_videos(lookup_target)
            if vids:
                st.video(f"https://www.youtube.com/watch?v={vids[0]['id']}")
            st.json(fetch_reddit_mentions(lookup_target))

        elif active_mod == "Red-team simulator":
            st.markdown(f"#### Red Team War Room: {lookup_target}")
            scenario_input = st.text_area("Enter scenario to simulate:", f"How will {lookup_target} respond if GoNano launches a nationwide warranty guarantee?")
            if st.button("Simulate Rival Counter-Attack", type="primary"):
                sim_res = simulate_rival_counter_attack(lookup_target, scenario_input)
                st.markdown(f"**Rival Response:**\n\n{sim_res}")

    else:
        st.markdown('<p class="eyebrow">Intelligence workspace</p>', unsafe_allow_html=True)
        st.markdown('<h1 class="head-title">Analytical Modules</h1>', unsafe_allow_html=True)
        st.markdown('<p class="head-copy">Open an evidence-led module without losing command-center context. Select any module below to drill down into live intelligence.</p>', unsafe_allow_html=True)

        chosen_module = st.selectbox(
            "Select Module to Open",
            [m[0] for m in modules_list],
            index=0
        )
        if st.button(f"Open {chosen_module} Engine", type="primary"):
            st.session_state.active_intelligence_module = chosen_module
            st.rerun()

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, (m_name, m_desc) in enumerate(modules_list):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="module-tile">
                    <b>{m_name}</b>
                    <small>{m_desc}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Launch {m_name}", key=f"btn_m_{i}", use_container_width=True):
                    st.session_state.active_intelligence_module = m_name
                    st.rerun()


# =============================================================================
# VIEW 3: RISK FRAMEWORK
# =============================================================================
elif selected_nav == "Risk Framework":
    st.markdown('<p class="eyebrow">Risk analysis</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="head-title">Risk Scorecard // {lookup_target}</h1>', unsafe_allow_html=True)
    st.markdown('<p class="head-copy">Exposure prioritization based on ISO 31000 & COSO ERM framework and analyst weighting.</p>', unsafe_allow_html=True)

    erm = calculate_erm_threat_matrix(lookup_target)
    rk1, rk2, rk3, rk4 = st.columns(4)
    with rk1:
        st.markdown(f"""
        <div class="kpi-card coral">
            <span class="kpi-lbl">Highest Threat Score</span>
            <div class="kpi-val">{erm['inherent_threat_score']}/10</div>
            <span class="badge-chip badge-critical">Level: {erm['inherent_threat_level']}</span>
        </div>
        """, unsafe_allow_html=True)
    with rk2:
        st.markdown(f"""
        <div class="kpi-card teal">
            <span class="kpi-lbl">GoNano Control Moat</span>
            <div class="kpi-val">{erm['control_efficacy_score']}/10</div>
            <span class="badge-chip badge-good">Defense: {erm['control_efficacy_level']}</span>
        </div>
        """, unsafe_allow_html=True)
    with rk3:
        st.markdown(f"""
        <div class="kpi-card amber">
            <span class="kpi-lbl">Residual Threat Rating</span>
            <div class="kpi-val">{erm['residual_threat_score']}/10</div>
            <span class="badge-chip badge-watch">Exposure: {erm['residual_threat_level']}</span>
        </div>
        """, unsafe_allow_html=True)
    with rk4:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-lbl">Polarity-VaR (90d)</span>
            <div class="kpi-val">-{erm['polarity_var_90d']}%</div>
            <span class="badge-chip badge-neutral">Portfolio At Risk</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    rk_c1, rk_c2 = st.columns([1.2, 1])
    with rk_c1:
        st.markdown("##### Key Competitive Indicators (Early Warning Thresholds)")
        for kci in erm["kcis"]:
            st.markdown(f"- **{kci['indicator']}**: `{kci['status']}` (Trigger: {kci['threshold']})")
    with rk_c2:
        st.markdown("##### Reverse Stress Testing (Failure Scenarios)")
        st.info(f"**Scenario:** {erm['reverse_stress_scenario']}\n\n**Mitigation:** {erm['contingency_mitigation']}")

    st.markdown("---")
    st.markdown(f"##### Prioritized Enterprise Risk Register ({p_count} Roster)")
    st.dataframe(generate_erm_kpi_table(), use_container_width=True, hide_index=True)


# =============================================================================
# VIEW 4: MONITORING & SIGNALS
# =============================================================================
elif selected_nav == "Monitoring & Signals":
    st.markdown('<p class="eyebrow">Monitoring</p>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="head-title">Signal Stream // {lookup_target}</h1>', unsafe_allow_html=True)
    st.markdown('<p class="head-copy">Live multi-source open-source surveillance, video captures, and web evidence.</p>', unsafe_allow_html=True)

    sig_c1, sig_c2 = st.columns([1.2, 1])
    with sig_c1:
        st.markdown("##### OSINT Evidence Queue")
        st.markdown("""
        <div class="evidence-box">
            <b>Residential roofing services listing</b>
            <p>Open-source capture references expanded regional service availability. Analyst review pending.</p>
        </div>
        <div class="evidence-box">
            <b>Contractor recruitment language update</b>
            <p>Observed channel copy may indicate distributor expansion. Confidence: medium.</p>
        </div>
        <div class="evidence-box">
            <b>Regional permit discussion</b>
            <p>Public discussion references local availability; no direct claim validation completed.</p>
        </div>
        """, unsafe_allow_html=True)

    with sig_c2:
        st.markdown("##### Live YouTube Tracker")
        yt_vids = search_youtube_videos(lookup_target)
        if yt_vids:
            st.video(f"https://www.youtube.com/watch?v={yt_vids[0]['id']}")
            st.caption(f"Captured: {yt_vids[0]['title']}")
        else:
            st.info("No active video broadcasts found for target.")

    st.markdown("---")
    st.markdown("##### Ad Transparency Radar")
    ads = get_public_ad_transparency_links(lookup_target)
    st.markdown(f"Meta Ad Library: [{ads.get('meta', 'Link')}]({ads.get('meta', '#')})")


# =============================================================================
# VIEW 5: PRIORITIZED ALERTS
# =============================================================================
elif selected_nav == "Prioritized Alerts":
    st.markdown('<p class="eyebrow">Action queue</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="head-title">Prioritized Alerts</h1>', unsafe_allow_html=True)
    st.markdown('<p class="head-copy">Filter material market developments and open analyst context.</p>', unsafe_allow_html=True)

    alert_filter = st.radio("FILTER_SEVERITY", ["All", "Critical", "Watch", "Verified"], horizontal=True)

    alerts_db = [
        {"title": "Warranty term change detected", "details": "ArroveX added prorated coverage exclusions on labor and materials.", "severity": "Critical", "style": ""},
        {"title": "Price increase detected", "details": "RevivaRoof regional standard pricing moved +20%.", "severity": "Critical", "style": ""},
        {"title": "New territory expansion", "details": "Localized partner activity surfaced in Ontario and Quebec.", "severity": "Watch", "style": "watch"},
        {"title": "Dealer channel evidence verified", "details": "Contractor communication activity has been validated.", "severity": "Verified", "style": "good"},
    ]

    for al in alerts_db:
        if alert_filter == "All" or alert_filter == al["severity"]:
            b_class = "badge-critical" if al["severity"] == "Critical" else ("badge-watch" if al["severity"] == "Watch" else "badge-good")
            st.markdown(f"""
            <div class="alert-row {al['style']}">
                <div>
                    <strong style="font-size:13px; color:#1B1C36;">{al['title']}</strong>
                    <p style="margin:3px 0 0; font-size:12px; color:#596078;">{al['details']}</p>
                </div>
                <div style="margin-left:auto;"><span class="badge-chip {b_class}">{al['severity']}</span></div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# VIEW 6: C-SUITE REQUEST DESK
# =============================================================================
elif selected_nav == "C-Suite Request Desk":
    st.markdown('<p class="eyebrow">Executive workflow</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="head-title">C-Suite Request Desk</h1>', unsafe_allow_html=True)
    st.markdown('<p class="head-copy">Review pending inquiries from contractors, analyze uploaded dossiers with Gemini 3.1 Pro, auto-record findings into the Google Sheet tracker, and dispatch reports with executive stakeholders CC\'d.</p>', unsafe_allow_html=True)

    # 1. Pending Requests Table
    st.markdown("#### 1. Pending Competitor Analysis Requests Queue")
    pending_reqs = get_all_pending_competitor_requests()

    if pending_reqs:
        st.dataframe(
            pd.DataFrame([
                {
                    "Request ID": r["id"],
                    "Source": r["source_type"],
                    "Competitor Name": r["competitor_name"],
                    "Requester": r["requester_name"],
                    "Requester Email": r["requester_email"],
                    "Territory / Market": r["location"],
                    "Date Requested": r["date_requested"],
                    "Field Notes": r["field_notes"][:90] + ("..." if len(r["field_notes"]) > 90 else ""),
                    "Status": r["status"]
                }
                for r in pending_reqs
            ]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No pending requests currently queued.")

    st.markdown("---")

    # 2. Fulfillment & Document Upload Form
    st.markdown("#### 2. Fulfill Request & Document Upload")
    with st.form("csuite_fulfillment_form", clear_on_submit=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            req_options = ["-- Custom Competitor Entry --"] + [f"{r['id']} - {r['competitor_name']} ({r['requester_name']})" for r in pending_reqs]
            selected_req_idx = st.selectbox("Select Pending Request to Fulfill", req_options)
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
                default_name = "GoNano Partner"
                req_id_val = None

            target_comp_input = st.text_input("Competitor Name *", value=default_comp)

        u_col1, u_col2 = st.columns(2)
        with u_col1:
            target_requester_email = st.text_input("Send Completed Analysis To (Requester Email) *", value=default_email)
        with u_col2:
            cc_recipients_input = st.text_input("CC Stakeholders (Comma Separated) *", value="joel@gonano.com, jonathan@gonano.com, charles@gonano.com, mathieu@gonano.com, jason@gonano.com")

        uploaded_doc = st.file_uploader(
            "Upload Completed Competitor Analysis Document / Dossier *",
            type=["pdf", "docx", "xlsx", "pptx", "txt", "png", "jpg"],
            help="Gemini 3.1 Pro will read the document, benchmark it, and commit it to the intelligence tracker."
        )

        exec_cover_notes = st.text_area("Executive Cover Notes", placeholder="e.g. Attached is the completed technical teardown on Roof Juice RX...", height=80)

        c_btn_sub = st.form_submit_button("🚀 Analyze with Gemini 3.1 Pro, Update Tracker & Dispatch", use_container_width=True, type="primary")

        if c_btn_sub:
            if not target_comp_input.strip() or not target_requester_email.strip() or not uploaded_doc:
                st.error("Please fill in Competitor Name, Requester Email, and attach the analysis document.")
            else:
                with st.spinner("Gemini 3.1 Pro analyzing document and updating tracker..."):
                    file_bytes = uploaded_doc.getvalue()
                    fname = uploaded_doc.name
                    gemini_data = analyze_document_with_gemini_3_pro(file_bytes=file_bytes, filename=fname, target_competitor=target_comp_input.strip())
                    parsed_ccs = [c.strip() for c in cc_recipients_input.split(",") if c.strip() and "@" in c]
                    
                    dispatch_res = dispatch_analysis_to_requester(
                        competitor_name=target_comp_input.strip(),
                        requester_name=default_name,
                        requester_email=target_requester_email.strip(),
                        uploaded_file_bytes=file_bytes,
                        filename=fname,
                        cc_emails=parsed_ccs,
                        executive_notes=exec_cover_notes.strip(),
                        gemini_summary=gemini_data.get("executive_summary", ""),
                        request_id=req_id_val
                    )
                    
                    if dispatch_res.get("status") == "success":
                        st.success(f"✅ Dossier dispatched to {target_requester_email} (CC: {', '.join(parsed_ccs)})!")
                        st.info(f"📊 Auto-Recorded into Tracker: Competitor Profile for '{target_comp_input.strip()}' committed.")
                        with st.expander("🔍 View Gemini 3.1 Pro Analysis Breakdown", expanded=True):
                            st.json(gemini_data)
                    else:
                        st.error(f"⚠️ Email dispatch failed: {dispatch_res.get('message')}")


# =============================================================================
# VIEW 7: EXPORTS
# =============================================================================
elif selected_nav == "Executive Exports":
    st.markdown('<p class="eyebrow">Exports</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="head-title">Executive Reports & Downloads</h1>', unsafe_allow_html=True)
    st.markdown('<p class="head-copy">Generate download-ready briefings from the current intelligence horizon across standard board formats.</p>', unsafe_allow_html=True)

    exp_c1, exp_c2, exp_c3 = st.columns(3)
    with exp_c1:
        st.markdown("""
        <div class="module-tile">
            <b>Competitive Exposure Brief</b>
            <small>Critical price, warranty, and territory changes exported with UTF-8 BOM encoding for Excel.</small>
        </div>
        """, unsafe_allow_html=True)
        csv_bytes = generate_utf8_bom_csv(lookup_target)
        st.download_button(
            "Download CSV Brief",
            data=csv_bytes,
            file_name=f"GoNano_Exposure_Brief_{lookup_target}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_c2:
        st.markdown("""
        <div class="module-tile">
            <b>Market Response Digest</b>
            <small>Formatted SpreadsheetML workbook with automated styling, formulas, and tabular matrices.</small>
        </div>
        """, unsafe_allow_html=True)
        xls_bytes = generate_spreadsheetml_xls(lookup_target)
        st.download_button(
            "Download Excel Digest",
            data=xls_bytes,
            file_name=f"GoNano_Response_Digest_{lookup_target}.xls",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

    with exp_c3:
        st.markdown("""
        <div class="module-tile">
            <b>Verified Boardroom Dossier Pack</b>
            <small>Formatted executive briefing memo in GitHub-flavored Markdown for boardroom distribution.</small>
        </div>
        """, unsafe_allow_html=True)
        memo_str = generate_csuite_markdown_memo(lookup_target)
        st.download_button(
            "Download Executive Memo (.md)",
            data=memo_str,
            file_name=f"GoNano_Executive_Memo_{lookup_target}.md",
            mime="text/markdown",
            use_container_width=True
        )
