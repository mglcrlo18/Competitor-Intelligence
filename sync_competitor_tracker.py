"""
sync_competitor_tracker.py
Extracts and merges all competitors and reports from the Google Sheet (Competitor Report Tracker)
into competitor_store.db, updating competitor_profiles and tracker_reports.
"""
import os
import sqlite3
import zipfile
import xml.etree.ElementTree as ET

DB_PATH = os.path.join(os.path.dirname(__file__), "competitor_store.db")
XLSX_PATH = os.path.join(os.path.dirname(__file__), "competitor_tracker.xlsx")

def run_sync():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create tracker_reports table
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
    # CRITICAL FIX: Removed "DELETE FROM tracker_reports" to prevent wiping Gemini Teardowns
    # every night during the background sync. We now only UPSERT or APPEND.

    # 2. Parse XLSX
    with zipfile.ZipFile(XLSX_PATH) as z:
        sst_xml = z.read('xl/sharedStrings.xml')
        sst_root = ET.fromstring(sst_xml)
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        shared_strings = []
        for si in sst_root.findall('main:si', ns):
            text = ''.join(t.text or '' for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'))
            shared_strings.append(text)

        def parse_sheet(sheet_path):
            xml_data = z.read(sheet_path)
            root = ET.fromstring(xml_data)
            rows_data = []
            for row in root.findall('.//main:row', ns):
                row_vals = {}
                for c in row.findall('main:c', ns):
                    r = c.attrib.get('r')
                    col = ''.join(filter(str.isalpha, r))
                    t = c.attrib.get('t')
                    v = c.find('main:v', ns)
                    val = v.text if v is not None else ''
                    if t == 's' and val.isdigit():
                        val = shared_strings[int(val)]
                    row_vals[col] = val
                rows_data.append(row_vals)
            return rows_data

        sheet1 = parse_sheet('xl/worksheets/sheet1.xml')
        sheet2 = parse_sheet('xl/worksheets/sheet2.xml')

    competitors = {}

    # Domain dictionary heuristic
    domain_map = {
        "RoofLife Canada": "rooflifecanada.com",
        "RoofLife": "rooflifecanada.com",
        "RoofLife (CA)": "rooflifecanada.com",
        "Nasiol": "nasiol.com",
        "Nasiol (Artekya)": "nasiol.com",
        "Nasiol Industrial Protection": "nasiol.com",
        "Reviva Roof": "revivaroof.com",
        "RevivaRoof": "revivaroof.com",
        "Spray-Net": "spray-net.com",
        "Spray-Net (Liqua-Roof)": "spray-net.com",
        "Armovex": "armovex.com",
        "ArmoveX": "armovex.com",
        "Zinox Coating": "zinoxcoating.com",
        "Z-Shield": "zinoxcoating.com",
        "Z-Shield / Zinox Coating": "zinoxcoating.com",
        "Roof Maxx": "roofmaxx.com",
        "SuperMaxx": "roofmaxx.com",
        "FreshRoof": "freshroof.com",
        "PEAK301": "peak301.com",
        "Sure Roof Pros": "sureroofpros.com",
        "Ever Roof": "everroof.com",
        "OnYa Roof": "onyaroof.com",
        "Roof Medixx": "roofmedixx.com",
        "NXCanada": "nxcanada.com",
        "NexaNano": "nexanano.com",
        "NoxNano (Noxor)": "noxor.ca",
        "Nanoclad": "nanoclad.com",
        "Nanoroof": "nanoroof.com",
        "Nano Protection AJ": "nanoprotectionaj.com",
        "Nano Protection AJ (revision: add Nano Revive)": "nanoprotectionaj.com",
        "Nano-Seal (US, Florida)": "nano-seal.com",
        "NanoSeal (Quebec)": "nanoseal.ca",
        "Nano-Toiture": "nano-toiture.com",
        "NanoGuard Systems": "nanoguardsystems.com",
        "Natural Seal": "naturalseal.ca",
        "Groupe GVMA": "scellant-toiture.com",
        "Groupe GVMA (Scellant-Toiture)": "scellant-toiture.com",
        "Roof Scientist": "roofscientist.ca",
        "Roof Scientist (re: Cericade)": "roofscientist.ca",
        "HydraChem": "hydrachemcoatings.com",
        "DuraSeal": "durasealroofing.com",
        "Purepave": "purepave.ca",
        "Rejuva Roof": "rejuvaroof.com",
        "Reactiv8": "reactiv8roofing.com",
        "Roof Rehab": "roofrehab.com",
        "Roof Rejuvenate": "roofrejuvenate.com",
        "Roof Savers": "roofsavers.com",
        "Roof Savers, LLC": "roofsavers.com",
        "Shingle RX": "shinglerx.com",
        "ShingleGuard": "shingleguard.com",
        "UglyRoof": "uglyroof.com",
        "Rhino Shield": "rhinoshield.com",
        "Équipe Nano": "equipenano.com",
        "TEAM NANO (Quebec)": "equipenano.com",
        "Bright Green Roof": "brightgreenroof.com",
        "MK Construction": "mkconstruction.ca",
        "NWA Restore It": "nwarestoreit.com",
        "Evolushingle": "evolushingle.com",
        "J&J Roof Restore": "jjroofrestore.com",
        "Inexso": "inexso.ca",
        "Roof Shield": "roofshield.com",
        "Roof Juice RX": "roofjuicerx.com",
        "Protège ton toit": "protegetontoit.com",
        "Les Gars Nano": "lesgarsnano.ca",
        "Southwest Roof": "southwestroof.com",
        "Quebec Competitor Analysis (Nano & Soy imposters)": "quebec-competitors.ca"
    }

    # Category heuristic
    def deduce_category_tech(name):
        n = name.lower()
        if any(x in n for x in ["maxx", "bio", "soy", "juice", "fresh", "rejuva", "evolushing", "bright green"]):
            return (
                "Topical Bio-Oil Roof Rejuvenator",
                "Agricultural ester / bio-oil spray (topical softening)",
                7.2, 6.0, 4.8, "US Sunbelt & Midwest"
            )
        elif any(x in n for x in ["nano", "clad", "nasiol", "zinox", "shield", "cericade", "hydra"]):
            return (
                "Nanotechnology / Surface Coating",
                "SiO2/Silica or liquid polymer barrier coating",
                6.5, 7.0, 3.5, "North America & International"
            )
        elif any(x in n for x in ["spray-net", "paint", "rhino", "ugly", "duraseal"]):
            return (
                "Architectural & Elastomeric Coatings",
                "Polymeric / acrylic on-site elastomeric finish",
                5.8, 7.5, 2.8, "Franchise & Contractor Network"
            )
        else:
            return (
                "Roof Restoration & Preservation",
                "Surface sealant / restoration treatment",
                5.5, 6.8, 3.0, "Regional North America"
            )

    # Insert Reports Sent
    for r in sheet1[1:]:
        comp = r.get('B', '').strip()
        if not comp: continue
        rep_type = r.get('C', '').strip()
        date_sent = r.get('D', '').strip()
        subject = r.get('E', '').strip()
        attachment = r.get('F', '').strip()
        to_rec = r.get('G', '').strip()
        cc_rec = r.get('H', '').strip()
        req_by = r.get('I', '').strip()
        req_date = r.get('J', '').strip()
        gmail_link = r.get('K', '').strip()
        drive_link = r.get('L', '').strip()
        notes = r.get('M', '').strip()

        cursor.execute("SELECT id FROM tracker_reports WHERE competitor = ? AND subject = ? AND date_pht = ?", (comp, subject, date_sent))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO tracker_reports (
                competitor, report_type, date_pht, subject, attachment_name,
                to_recipients, cc_recipients, requested_by, request_date,
                gmail_link, drive_link, status, notes, sheet_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (comp, rep_type, date_sent, subject, attachment, to_rec, cc_rec, req_by, req_date, gmail_link, drive_link, "Report Sent", notes, "Reports Sent"))

        if comp not in competitors:
            cat, tech, inh, ctrl, res, reg = deduce_category_tech(comp)
            competitors[comp] = {
                "name": comp,
                "domain": domain_map.get(comp, f"{comp.lower().replace(' ', '')}.com"),
                "category": cat,
                "core_technology": tech,
                "inherent_threat_score": inh,
                "control_efficacy_score": ctrl,
                "residual_threat_score": res,
                "target_regions": reg,
                "report_status": f"Report Sent ({rep_type})",
                "reports_count": 0,
                "latest_report_date": date_sent,
                "notes": notes,
                "source_sheet": "Reports Sent",
                "gmail_link": gmail_link
            }
        competitors[comp]["reports_count"] += 1
        if date_sent and date_sent > (competitors[comp]["latest_report_date"] or ""):
            competitors[comp]["latest_report_date"] = date_sent

    # Insert Open Requests
    for r in sheet2[1:]:
        comp = r.get('B', '').strip()
        if not comp: continue
        web = r.get('C', '').strip()
        req_by = r.get('D', '').strip()
        req_date = r.get('E', '').strip()
        channel = r.get('F', '').strip()
        summary = r.get('G', '').strip()
        gmail_link = r.get('H', '').strip()
        status = r.get('I', '').strip() or "Open"
        notes = r.get('J', '').strip()

        cursor.execute("SELECT id FROM tracker_reports WHERE competitor = ? AND subject = ? AND request_date = ?", (comp, summary, req_date))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO tracker_reports (
                competitor, report_type, date_pht, subject, attachment_name,
                to_recipients, cc_recipients, requested_by, request_date,
                gmail_link, drive_link, status, notes, sheet_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (comp, "Open Request", req_date, summary, "", "", "", req_by, req_date, gmail_link, "", status, notes, "Open Requests"))

        if comp not in competitors:
            cat, tech, inh, ctrl, res, reg = deduce_category_tech(comp)
            competitors[comp] = {
                "name": comp,
                "domain": web or domain_map.get(comp, f"{comp.lower().replace(' ', '')}.com"),
                "category": cat,
                "core_technology": tech,
                "inherent_threat_score": inh,
                "control_efficacy_score": ctrl,
                "residual_threat_score": res,
                "target_regions": "Quebec / Canada" if "quebec" in comp.lower() or "nano" in comp.lower() else reg,
                "report_status": f"Open Request ({status})",
                "reports_count": 0,
                "latest_report_date": req_date,
                "notes": notes or summary,
                "source_sheet": "Open Requests",
                "gmail_link": gmail_link
            }
        else:
            if web:
                competitors[comp]["domain"] = web
            if notes:
                competitors[comp]["notes"] = (competitors[comp]["notes"] + " | " + notes).strip(" | ")

    # Ensure GoNano is in competitor_profiles
    if "GoNano (Your Brand)" not in competitors:
        competitors["GoNano (Your Brand)"] = {
            "name": "GoNano (Your Brand)",
            "domain": "gonano.com",
            "category": "Molecular Substrate Nanotechnology",
            "core_technology": "Silica/Alumina covalent molecular matrix integration",
            "inherent_threat_score": 2.0,
            "control_efficacy_score": 9.2,
            "residual_threat_score": 1.1,
            "target_regions": "North America (US & Canada)",
            "report_status": "Internal Baseline",
            "reports_count": 0,
            "latest_report_date": "2026-09-28",
            "notes": "GoNano proprietary patented technology.",
            "source_sheet": "Baseline",
            "gmail_link": "https://gonano.com"
        }

    # Upsert all into competitor_profiles
    for name, c in competitors.items():
        cursor.execute("SELECT id FROM competitor_profiles WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
            UPDATE competitor_profiles SET
                domain = ?,
                category = ?,
                core_technology = ?,
                target_regions = ?,
                report_status = ?,
                reports_count = ?,
                latest_report_date = ?,
                notes = ?,
                source_sheet = ?,
                gmail_link = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE name = ?
            """, (
                c["domain"], c["category"], c["core_technology"], c["target_regions"],
                c["report_status"], c["reports_count"], c["latest_report_date"],
                c["notes"], c["source_sheet"], c["gmail_link"], name
            ))
        else:
            cursor.execute("""
            INSERT INTO competitor_profiles (
                name, domain, category, core_technology, inherent_threat_score,
                control_efficacy_score, residual_threat_score, target_regions,
                report_status, reports_count, latest_report_date, notes,
                source_sheet, gmail_link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, c["domain"], c["category"], c["core_technology"],
                c["inherent_threat_score"], c["control_efficacy_score"], c["residual_threat_score"],
                c["target_regions"], c["report_status"], c["reports_count"],
                c["latest_report_date"], c["notes"], c["source_sheet"], c["gmail_link"]
            ))

    # Seed rich marketing gap dossiers for new competitors
    extra_gaps = [
        ("Roof Maxx", "Restores Shingle Flexibility with 80% Cost Savings", "Website & Broadcast Ads", "Independent tests show topical methyl soyate softens top layer but washes away under thermal rain cycling.", "Roofing Contractor Forensics", "HIGH", 75.0, "https://roofmaxx.com", "Contrast temporary topical bio-oil with GoNano permanent silica molecular cross-linking."),
        ("FreshRoof", "Natural Agricultural Oil Rejuvenation with 6-Year Guarantee", "Franchise Marketing Portal", "Homeowners report greasy shingle sheen and oil film washing onto landscaping during spring storms.", "Better Business Bureau & Forum", "HIGH", 73.0, "https://freshroof.com", "Highlight GoNano clean, solvent-free, non-greasy molecular application."),
        ("PEAK301", "Nano-Enhanced Rejuvenation Breakthrough", "Dealer Presentation Decks", "Marketing claims nano performance but chemical composition relies heavily on bio-based carrier oils.", "Chemical Testing Laboratory", "MODERATE", 65.0, "https://peak301.com", "Demand ASTM D3462 third-party tensile tear strength proof."),
        ("Sure Roof Pros", "Lifetime Roof Protection and Restoration", "Direct Sales Proposals", "Terms contain heavy prorated depreciation exclusions for roofs older than 12 years.", "Homeowner Contract Reviews", "CRITICAL", 81.0, "https://sureroofpros.com", "Expose prorated warranty clauses and position GoNano comprehensive 15-year warranty."),
        ("Protège ton toit", "Quebec's Exclusive Nano Restoration System", "Local Social Campaigns", "Directly replicates competitor can designs and marketing claims without verified formulation certifications.", "Quebec Contractor Registry", "HIGH", 78.0, "https://protegetontoit.com", "Submit to legal for IP enforcement and educate regional contractors on genuine GoNano certifications."),
        ("Les Gars Nano", "Advanced Nano Surface Preservation for Roofing", "Regional Web & Social", "Added to GoNano IP infringement tracker due to trademark and brand confusion in Quebec.", "Legal Trademark Register", "HIGH", 74.0, "https://lesgarsnano.ca", "Maintain brand exclusivity and certified applicator dealer network in Quebec."),
        ("Inexso", "Next-Gen Shingle Life Extension System", "Trade Show Exhibits", "Trade show promotion lacks certified laboratory testing data or ASTM compliance documentation.", "Trade Show Engineering Review", "MODERATE", 60.0, "https://inexso.ca", "Challenge estimators on ASTM D3161 wind uplift and Class 3/4 impact ratings."),
        ("Roof Shield", "Complete Barrier Protection Against UV and Rain", "Dealer Catalog", "Topical barrier creates moisture-trapping skin over aged shingles rather than deep substrate rejuvenation.", "Forensic Roofing Audits", "HIGH", 69.0, "https://roofshield.com", "Demonstrate that GoNano is breathable at the nanoscale, letting moisture escape while locking in strength.")
    ]

    for comp, claim, ch, real, src, sev, score, url, take in extra_gaps:
        cursor.execute("SELECT id FROM marketing_gap_records WHERE competitor = ? AND marketing_claim = ?", (comp, claim))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO marketing_gap_records (
                competitor, marketing_claim, claim_channel, customer_reality,
                reality_source, gap_severity, divergence_score, source_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (comp, claim, ch, real, src, sev, score, url))

    conn.commit()
    
    # Summary
    cursor.execute("SELECT COUNT(*) FROM competitor_profiles")
    total_profiles = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tracker_reports")
    total_reports = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM marketing_gap_records")
    total_gaps = cursor.fetchone()[0]
    conn.close()

    print(f"Sync complete! Database now has:")
    print(f" - {total_profiles} competitor profiles")
    print(f" - {total_reports} tracker report records from Google Sheets")
    print(f" - {total_gaps} marketing gap dossiers")

if __name__ == "__main__":
    run_sync()
