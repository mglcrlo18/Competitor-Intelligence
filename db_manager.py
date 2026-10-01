"""
db_manager.py
Embedded SQLite Persistence Engine for Competitor Intelligence Platform.
Stores signals, competitor profiles, pricing updates, customer reviews,
marketing gap dossiers, ERM evaluations, and Google Sheets tracker records.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "competitor_store.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Signals & Mentions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        competitor TEXT NOT NULL,\n        platform TEXT NOT NULL,\n        channel_badge TEXT,\n        author TEXT,\n        title TEXT NOT NULL,\n        snippet TEXT,\n        sentiment TEXT DEFAULT 'Neutral',\n        polarity REAL DEFAULT 0.0,\n        url TEXT,\n        timestamp TEXT,\n        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n    )
    """)
    
    # 2. Competitor Corporate & Strategy Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_profiles (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        name TEXT UNIQUE NOT NULL,\n        domain TEXT,\n        category TEXT,\n        core_technology TEXT,\n        inherent_threat_score REAL DEFAULT 5.0,\n        control_efficacy_score REAL DEFAULT 5.0,\n        residual_threat_score REAL DEFAULT 2.5,\n        target_regions TEXT,\n        report_status TEXT,\n        reports_count INTEGER DEFAULT 0,\n        latest_report_date TEXT,\n        notes TEXT,\n        source_sheet TEXT,\n        gmail_link TEXT,\n        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP\n    )
    """)
    
    # 3. Pricing & Commercial Claims
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pricing_records (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        competitor TEXT NOT NULL,\n        product_name TEXT NOT NULL,\n        price_model TEXT,\n        estimated_sqft_cost REAL,\n        claim_warranty_years INTEGER,\n        source_url TEXT,\n        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n    )
    """)
    
    # 4. Brand Promise vs Customer Reality (Marketing Gap)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_gap_records (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        competitor TEXT NOT NULL,\n        marketing_claim TEXT NOT NULL,\n        claim_channel TEXT,\n        customer_reality TEXT NOT NULL,\n        reality_source TEXT,\n        gap_severity TEXT DEFAULT 'MODERATE',\n        divergence_score REAL DEFAULT 50.0,\n        source_url TEXT,\n        strategic_takeaway TEXT,\n        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n    )
    """)
    
    # 5. ERM Risk & KCI Register
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS erm_risk_register (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        competitor TEXT NOT NULL,\n        risk_category TEXT NOT NULL,\n        inherent_threat TEXT NOT NULL,\n        control_defense TEXT NOT NULL,\n        residual_threat TEXT NOT NULL,\n        kci_early_warning TEXT NOT NULL,\n        reverse_stress_scenario TEXT NOT NULL,\n        var_downside_pct REAL DEFAULT 15.0,\n        created_at DATETIME DEFAULT CURRENT_TIMESTAMP\n    )
    """)

    # 6. Google Sheets Tracker Reports (Reports Sent & Open Requests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracker_reports (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        competitor TEXT NOT NULL,\n        report_type TEXT,\n        date_pht TEXT,\n        subject TEXT,\n        attachment_name TEXT,\n        to_recipients TEXT,\n        cc_recipients TEXT,\n        requested_by TEXT,\n        request_date TEXT,\n        gmail_link TEXT,\n        drive_link TEXT,\n        status TEXT,\n        notes TEXT,\n        sheet_name TEXT\n    )
    """)
    
    # Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_comp ON signals (competitor)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_time ON signals (created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracker_comp ON tracker_reports (competitor)")
    
    conn.commit()
    conn.close()

def seed_baseline_data():
    """Populates baseline intelligence dossiers and syncs sheet data if needed."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM competitor_profiles")
    count = cursor.fetchone()["count"]
    conn.close()

    if count < 20:
        try:
            import sync_competitor_tracker
            sync_competitor_tracker.run_sync()
        except Exception as e:
            print(f"Error seeding competitor tracker data: {e}")

def get_all_competitor_names() -> List[str]:
    """Returns sorted list of all competitor names in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM competitor_profiles ORDER BY name ASC")
    names = [r["name"] for r in cursor.fetchall() if r["name"]]
    conn.close()
    if not names:
        names = ["RoofLife Canada", "Nasiol (Artekya)", "RevivaRoof", "Spray-Net", "ArmoveX", "Zinox Coating", "GoNano (Your Brand)"]
    return names

def get_all_monitored_competitors() -> List[Dict[str, str]]:
    """Returns list of all competitors with their domains for background monitoring."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, domain FROM competitor_profiles WHERE name != 'GoNano (Your Brand)' ORDER BY name ASC")
    rows = []
    for r in cursor.fetchall():
        name = r["name"]
        domain = r["domain"] or f"{name.lower().replace(' ', '')}.com"
        rows.append({"name": name, "domain": domain})
    conn.close()
    return rows

def get_competitor_profile(name: Optional[str]) -> Optional[Dict[str, Any]]:
    """Retrieves full profile for a competitor by exact or partial match."""
    if not name or not str(name).strip():
        return None
    name = str(name).strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitor_profiles WHERE LOWER(name) = LOWER(?)", (name.strip(),))
    row = cursor.fetchone()
    if not row:
        cursor.execute("SELECT * FROM competitor_profiles WHERE LOWER(name) LIKE ? LIMIT 1", (f"%{name.strip().lower()}%",))
        row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_competitor_profiles() -> List[Dict[str, Any]]:
    """Returns all competitor profile records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM competitor_profiles ORDER BY inherent_threat_score DESC, name ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_tracker_reports(competitor: Optional[str] = None, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns historical competitor reports sent or open requests from the Google Sheet."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM tracker_reports WHERE 1=1"
    params = []
    if competitor and competitor != "All Competitors":
        query += " AND (LOWER(competitor) LIKE ? OR LOWER(?) LIKE '%' || LOWER(competitor) || '%')"
        params.extend([f"%{competitor.lower()}%", competitor.lower()])
    if sheet_name:
        query += " AND sheet_name = ?"
        params.append(sheet_name)
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def add_custom_competitor(name: str, domain: str, category: str, notes: str = "") -> bool:
    """Adds or updates a custom competitor to the monitored roster."""
    if not name or not name.strip():
        return False
    name = name.strip()
    domain = domain.strip() if domain else f"{name.lower().replace(' ', '')}.com"
    category = category.strip() if category else "Roof Restoration & Preservation"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO competitor_profiles (
        name, domain, category, core_technology, inherent_threat_score,
        control_efficacy_score, residual_threat_score, target_regions,
        report_status, notes, source_sheet
    ) VALUES (?, ?, ?, ?, 6.0, 7.0, 3.2, 'North America', 'Custom Monitored Target', ?, 'User Added')
    ON CONFLICT(name) DO UPDATE SET
        domain = excluded.domain,
        category = excluded.category,
        notes = excluded.notes,
        last_updated = CURRENT_TIMESTAMP
    """, (name, domain, category, f"{category} formulation", notes))
    conn.commit()
    conn.close()
    return True

def save_signals_to_db(signals_list: List[Dict[str, Any]], competitor: str):
    """Saves scraped signals safely to SQLite database."""
    if not signals_list:
        return
    conn = get_connection()
    cursor = conn.cursor()
    for s in signals_list:
        cursor.execute("""
        INSERT INTO signals (competitor, platform, channel_badge, author, title, snippet, sentiment, polarity, url, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            competitor,
            s.get("source", "Web"),
            s.get("channel_badge", s.get("source", "Web")),
            s.get("author", s.get("channel", "Unknown")),
            s.get("title", ""),
            s.get("snippet", ""),
            s.get("sentiment", "Neutral"),
            s.get("polarity", 0.0),
            s.get("url", "#"),
            s.get("published", s.get("timestamp", datetime.now().strftime("%Y-%m-%d")))
        ))
    conn.commit()
    conn.close()

def parse_signal_datetime(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    ts_clean = str(ts_str).strip()
    rel_match = re.match(r'(\d+)\s*(d|day|days|mo|month|months|y|year|years)\s*ago', ts_clean, re.I)
    if rel_match:
        val = int(rel_match.group(1))
        unit = rel_match.group(2).lower()
        now = datetime.now()
        if unit in ('d', 'day', 'days'):
            return now - timedelta(days=val)
        elif unit in ('mo', 'month', 'months'):
            return now - timedelta(days=val * 30)
        elif unit in ('y', 'year', 'years'):
            return now - timedelta(days=val * 365)
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(ts_clean[:19], fmt)
        except Exception:
            pass
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(ts_clean)
    except Exception:
        pass
    return None

def get_all_signals_for_competitor(competitor: Optional[str] = None, limit: int = 50, time_horizon: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if competitor and competitor != "All Competitors":
        cursor.execute("""
        SELECT * FROM signals WHERE LOWER(competitor) LIKE ? ORDER BY id DESC LIMIT 150
        """, (f"%{competitor.lower()}%",))
    else:
        cursor.execute("""
        SELECT * FROM signals ORDER BY id DESC LIMIT 150
        """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not time_horizon or str(time_horizon).lower() in ("all", "all time"):
        return rows[:limit]

    th = str(time_horizon).lower()
    max_days = 30
    if "24" in th or "1 day" in th or "today" in th:
        max_days = 1
    elif "7" in th:
        max_days = 7
    elif "30" in th:
        max_days = 30
    elif "90" in th:
        max_days = 90
    elif "12" in th or "year" in th:
        max_days = 365

    cutoff = datetime.now() - timedelta(days=max_days)
    filtered = []
    for r in rows:
        dt = parse_signal_datetime(r.get("timestamp"))
        if dt:
            if dt.tzinfo:
                dt = dt.replace(tzinfo=None)
            if dt >= cutoff:
                filtered.append(r)
    return filtered[:limit]


def get_marketing_gaps(competitor: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if competitor and competitor != "All Competitors":
        cursor.execute("""
        SELECT * FROM marketing_gap_records 
        WHERE LOWER(competitor) LIKE ? 
           OR LOWER(?) LIKE '%' || LOWER(competitor) || '%'
           OR LOWER(marketing_claim) LIKE ?
           OR LOWER(customer_reality) LIKE ?
        ORDER BY divergence_score DESC
        """, (f"%{competitor.lower()}%", competitor.lower(), f"%{competitor.lower()}%", f"%{competitor.lower()}%"))
    else:
        cursor.execute("SELECT * FROM marketing_gap_records ORDER BY divergence_score DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_erm_risks(competitor: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if competitor and competitor != "All Competitors":
        cursor.execute("SELECT * FROM erm_risk_register WHERE LOWER(competitor) LIKE ? ORDER BY var_downside_pct DESC", (f"%{competitor.lower()}%",))
    else:
        cursor.execute("SELECT * FROM erm_risk_register ORDER BY var_downside_pct DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# Initialize on import
init_db()
seed_baseline_data()
