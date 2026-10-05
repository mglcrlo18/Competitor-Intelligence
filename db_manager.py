"""
db_manager.py
Embedded SQLite Persistence Engine for Competitor Intelligence Platform.
Stores signals, competitor profiles, pricing updates, customer reviews,
marketing gap dossiers, ERM evaluations, and Google Sheets tracker records.
"""
import sqlite3
import os
import re
import email.utils
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
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
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT NOT NULL,
        platform TEXT NOT NULL,
        channel_badge TEXT,
        author TEXT,
        title TEXT NOT NULL,
        snippet TEXT,
        sentiment TEXT DEFAULT 'Neutral',
        polarity REAL DEFAULT 0.0,
        url TEXT,
        timestamp TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Competitor Corporate & Strategy Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS competitor_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        domain TEXT,
        category TEXT,
        core_technology TEXT,
        inherent_threat_score REAL DEFAULT 5.0,
        control_efficacy_score REAL DEFAULT 5.0,
        residual_threat_score REAL DEFAULT 2.5,
        target_regions TEXT,
        report_status TEXT,
        reports_count INTEGER DEFAULT 0,
        latest_report_date TEXT,
        notes TEXT,
        source_sheet TEXT,
        gmail_link TEXT,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Pricing & Commercial Claims
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pricing_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT NOT NULL,
        product_name TEXT NOT NULL,
        price_model TEXT,
        estimated_sqft_cost REAL,
        claim_warranty_years INTEGER,
        source_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 4. Brand Promise vs Customer Reality (Marketing Gap)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_gap_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT NOT NULL,
        marketing_claim TEXT NOT NULL,
        claim_channel TEXT,
        customer_reality TEXT NOT NULL,
        reality_source TEXT,
        gap_severity TEXT DEFAULT 'MODERATE',
        divergence_score REAL DEFAULT 50.0,
        source_url TEXT,
        strategic_takeaway TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 5. ERM Risk & KCI Register
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS erm_risk_register (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT NOT NULL,
        risk_category TEXT NOT NULL,
        inherent_threat TEXT NOT NULL,
        control_defense TEXT NOT NULL,
        residual_threat TEXT NOT NULL,
        kci_early_warning TEXT NOT NULL,
        reverse_stress_scenario TEXT NOT NULL,
        var_downside_pct REAL DEFAULT 15.0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Google Sheets Tracker Reports (Reports Sent & Open Requests)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tracker_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        competitor TEXT NOT NULL,
        report_type TEXT,
        date_pht TEXT,
        subject TEXT,
        attachment_name TEXT,
        to_recipients TEXT,
        cc_recipients TEXT,
        requested_by TEXT,
        request_date TEXT,
        gmail_link TEXT,
        drive_link TEXT,
        status TEXT,
        notes TEXT,
        sheet_name TEXT
    )
    """)
    
    # Indices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_comp ON signals (competitor)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_time ON signals (created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracker_comp ON tracker_reports (competitor)")
    
    conn.commit()
    conn.close()

def seed_pricing_records():
    """Populates pricing records table with verified competitor pricing data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM pricing_records")
    row = cursor.fetchone()
    count = row["count"] if row else 0
    if count < 10:
        cursor.execute("DELETE FROM pricing_records")
        verified_pricing = [
            ("GoNano (Your Brand)", "NuRoof Fortify / Revive / Boost", "Flat rate per residential roof tier ($3,500 - $6,000 total; 75-80% less than full replacement)", 1.10, 15, "https://gonano.com/en/shingle-technology"),
            ("Roof Maxx", "Soy Methyl Ester Bio-Oil", "Per sq.ft. (~$1.20/sq.ft. base; typical $3,000-$6,000; 20-25% of replacement)", 1.20, 5, "https://roofmaxx.com/warranty/"),
            ("PEAK301", "GreenSoy Formulation", "Per sq.ft. (Starts at ~$1.00/sq.ft.; estimated savings $1,530 vs replacement)", 1.00, 6, "https://peak301.com/"),
            ("Reactiv8", "Plant-Based Bio-Oil", "Flat rate / Per sq.ft. (~$2,300 for 600 sq.ft.; ~$3.83/sq.ft.)", 3.83, 5, "https://reactiv8inc.com/"),
            ("RoofLife Canada", "GreenSoy Treatment", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://rooflife.ca/free-quote/"),
            ("Shingle Magic", "Shingletech Acrylic Sealer", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 10, "https://shinglemagic.com/"),
            ("Nasiol (Artekya)", "Z-WB Industrial Coating", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 3, "https://shop.nasiol.com/en"),
            ("Spray-Net", "Liqua-Roof Elastomeric Paint", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 15, "https://spray-network.com/self-booking/?pathb=1&lang=en"),
            ("Rhino Shield", "Elastomeric Wall & Roof System", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 25, "https://rhinoshield.com/rhino-shield-pricing"),
            ("NoxNano (Noxor)", "Elite Shingle Package", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://noxor.ca/en/product/elite/"),
            ("Nanoclad", "Nanoclad Protection", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://nanoclad.ca/quote"),
            ("Ever Roof", "EverRoof Shingle System", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://everroof.co/request-a-quote/"),
            ("Bright Green Roof", "Bio-Roof Rejuvenation", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://brightgreenroof.com/get-a-quote"),
            ("MK Construction", "Quebec Restoration Soumission", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://www.mkconstruction.ca/soumission.html"),
            ("NexaNano", "NexaNano Roof Protect", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://roofguardpro.com/products/roof-protection/nexanano-roof-protect/"),
            ("OnYa Roof", "Contractor Business Packages", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://startrejuvenationbusiness.com/"),
            ("Roof Rejuvenate", "Residential Shingle Estimate", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://roofrejuvenate.com/Free-Estimate.html"),
            ("Roof Scientist (Cericade)", "Cericade Nano Coating", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://roofscientist.com/contact-us/"),
            ("ShingleGuard", "Consultation & Estimate", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 5, "https://shingleguard.ca/contact"),
            ("FreshRoof", "GreenSoy Bio-Rejuvenator", "Pricing Not Publicly Disclosed — Available via Field Sales Inquiries", 0.0, 6, "https://freshroof.com/")
        ]
        for comp, prod, model, cost, war, url in verified_pricing:
            cursor.execute("""
            INSERT INTO pricing_records (competitor, product_name, price_model, estimated_sqft_cost, claim_warranty_years, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (comp, prod, model, cost, war, url))
        conn.commit()
    conn.close()

def get_pricing_records(competitor: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns verified pricing records for competitors."""
    conn = get_connection()
    cursor = conn.cursor()
    if competitor and competitor != "All Competitors":
        cursor.execute("SELECT * FROM pricing_records WHERE LOWER(competitor) LIKE ? OR LOWER(?) LIKE '%' || LOWER(competitor) || '%'", (f"%{competitor.lower()}%", competitor.lower()))
    else:
        cursor.execute("SELECT * FROM pricing_records ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

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

    seed_pricing_records()

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

def normalize_signal_date(raw_date: Any) -> str:
    """Normalizes various date formats (RFC 2822, ISO, relative) to YYYY-MM-DD in PHT."""
    if not raw_date:
        return datetime.now(ZoneInfo("Asia/Manila")).strftime("%Y-%m-%d")
    raw_str = str(raw_date).strip()
    if not raw_str or raw_str.lower() in ["recent", "now", "today"]:
        return datetime.now(ZoneInfo("Asia/Manila")).strftime("%Y-%m-%d")

    # RFC 2822 (common in RSS)
    try:
        dt = email.utils.parsedate_to_datetime(raw_str)
        if dt:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # Relative date (e.g. '2 days ago', '5 hours ago')
    rel_match = re.match(r'(\d+)\s*(d|day|days|h|hour|hours)\s*ago', raw_str, re.I)
    if rel_match:
        val = int(rel_match.group(1))
        unit = rel_match.group(2).lower()
        now_pht = datetime.now(ZoneInfo("Asia/Manila"))
        if unit.startswith('d'):
            return (now_pht - timedelta(days=val)).strftime("%Y-%m-%d")
        elif unit.startswith('h'):
            return (now_pht - timedelta(hours=val)).strftime("%Y-%m-%d")

    # Standard formats
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%b %d, %Y', '%B %d, %Y', '%d %b %Y', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z'):
        try:
            return datetime.strptime(raw_str[:19] if 'T' in raw_str and 'Z' not in raw_str else raw_str, fmt).strftime('%Y-%m-%d')
        except Exception:
            pass

    return datetime.now(ZoneInfo("Asia/Manila")).strftime("%Y-%m-%d")

def save_signals_to_db(signals_list: List[Dict[str, Any]], competitor: str):
    """Saves scraped signals safely to SQLite database with URL resolution, schema normalization, and deduplication."""
    if not signals_list:
        return
    conn = get_connection()
    cursor = conn.cursor()
    for s in signals_list:
        raw_url = (s.get("url") or s.get("link") or "#").strip()
        title = (s.get("title") or "").strip()
        if not title:
            continue
        # Avoid duplicate signals by URL or title+competitor
        if raw_url and raw_url != "#":
            cursor.execute("SELECT id FROM signals WHERE competitor = ? AND (url = ? OR title = ?)", (competitor, raw_url, title))
        else:
            cursor.execute("SELECT id FROM signals WHERE competitor = ? AND title = ?", (competitor, title))
        if cursor.fetchone():
            continue

        platform = s.get("source") or s.get("platform") or "Industry Press"
        raw_date = s.get("published") or s.get("timestamp") or s.get("date")
        normalized_timestamp = normalize_signal_date(raw_date)
        snippet = (s.get("snippet") or s.get("summary") or "").strip()

        cursor.execute("""
        INSERT INTO signals (competitor, platform, channel_badge, author, title, snippet, sentiment, polarity, url, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            competitor,
            platform,
            s.get("channel_badge", platform),
            s.get("author", s.get("channel", "Unknown")),
            title,
            snippet,
            s.get("sentiment", "Neutral"),
            s.get("polarity", 0.0),
            raw_url,
            normalized_timestamp
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


def purge_expired_cached_reviews(max_age_days: int = 30) -> int:
    """
    Enforces compliance with Google Maps Platform Data Retention Terms of Service (Section 3.2.3).
    Automatically purges cached third-party review records and location metadata older than 30 days.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cutoff_date = (datetime.now() - timedelta(days=max_age_days)).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    DELETE FROM signals 
    WHERE (platform LIKE '%review%' OR channel_badge LIKE '%review%' OR title LIKE '%Rating%')
      AND created_at < ?
    """, (cutoff_date,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

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
