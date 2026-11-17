"""The weekly email may only contain what the scan found: no fixed claims, no junk news, no placeholder news."""
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import report_generator as rg  # noqa: E402

TODAY = datetime.now(ZoneInfo("Asia/Manila"))
D = lambda n: (TODAY - timedelta(days=n)).strftime("%Y-%m-%d")  # noqa: E731

BANNED = ["ASTM D3462", "15-Year", "evaporate", "Insurance adjusters", "washout", "HIGH THREAT",
          "PRIORITY ACTION", "patented", "permanent", "Neutralize bio-oil",
          "How Raising Prices Can Offset", "Surpasses 20,000 Customer Reviews"]

PROFILES = [{"name": n} for n in ["Roof Maxx", "Bright Green Roof", "Rejuva Roof", "NoxNano (Noxor)",
                                   "QA_Verification_Brand_2026", "QA_Test_NanoRoof_Solutions",
                                   "Quebec Competitor Analysis (Nano & Soy imposters)", "GoNano (Your Brand)"]]

JUNK = [
    # word match only: "bright green" planters on a house with a "peaked roof"
    ("Bright Green Roof", "News Publication", "Two-story underground house with peaked roof and balcony planters",
     "The video shows a completed two-story underground house with a peaked roof and bright green balcony planters.", D(1)),
    # QA fixture row
    ("QA_Verification_Brand_2026", "News Publication", "Sojern Scales Campaign Verification with Stellair's AI-Powered Screenshot Service",
     "Stellair automates screenshot capture and QA.", D(5)),
    # generic roofing article attached to a competitor it never names
    ("Rejuva Roof", "EIN Presswire", "Roofing Specialists Respond to Storm Damage Repair Needs in Southeast Michigan",
     "Local roofers respond to storm damage.", D(1)),
    # names the competitor but is not about roofing
    ("Roof Maxx", "Blog", "Roof Maxx sponsors a charity golf day", "Roof Maxx staff joined a golf tournament.", D(2)),
]
GOOD = [
    ("Roof Maxx", "Newswire", "From rejuvenation to restoration: Roof Maxx rebrands",
     "Roof Maxx says its plant-based treatment extends the life of asphalt shingle roofs.", D(2)),
    ("NoxNano (Noxor)", "Site", "Noxor lance NoxNano Élite pour les toitures",
     "Noxor offre une protection nano pour bardeau d'asphalte.", D(3)),
]


def _db(rows):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE signals (id INTEGER PRIMARY KEY, competitor TEXT, platform TEXT, title TEXT, snippet TEXT, timestamp TEXT, url TEXT)")
    for i, (c, p, t, s, d) in enumerate(rows):
        conn.execute("INSERT INTO signals (competitor, platform, title, snippet, timestamp, url) VALUES (?,?,?,?,?,?)",
                     (c, p, t, s, d, f"https://example.com/{i}"))
    conn.commit()
    return conn


def _build(monkeypatch, rows):
    conn = _db(rows)
    monkeypatch.setattr(rg, "get_connection", lambda: conn)
    monkeypatch.setattr(rg, "get_all_competitor_profiles", lambda: PROFILES)
    monkeypatch.delenv("DASHBOARD_URL", raising=False)
    return rg.build_executive_one_pager()


def test_no_fixed_claims_or_placeholder_news(monkeypatch):
    for rows in (JUNK + GOOD, JUNK, []):
        out = _build(monkeypatch, rows)
        for text in (out["html"], out["plain_text"]):
            for b in BANNED:
                assert b.lower() not in text.lower(), f"found '{b}'"


def test_junk_items_are_left_out_and_real_ones_kept(monkeypatch):
    out = _build(monkeypatch, JUNK + GOOD)
    t = out["plain_text"]
    assert "underground house" not in t
    assert "Stellair" not in t and "QA_VERIFICATION" not in t.upper()
    assert "Southeast Michigan" not in t
    assert "golf" not in t
    assert "Roof Maxx rebrands" in t
    assert "NoxNano" in t
    assert "NEWS ITEMS THAT PASSED THE CHECK THIS WEEK: 2" in t
    assert "4 other items from the scan were left out" in t


def test_says_so_when_nothing_passes(monkeypatch):
    out = _build(monkeypatch, JUNK)
    assert "No verified competitor news this week." in out["plain_text"]
    assert "No verified competitor news this week." in out["html"]
    assert "NEWS ITEMS THAT PASSED THE CHECK THIS WEEK: 0" in out["plain_text"]


def test_counts_exclude_test_rows(monkeypatch):
    out = _build(monkeypatch, GOOD)
    assert "TRACKED COMPETITORS: 4" in out["plain_text"]  # 8 rows minus 3 test/notes rows and GoNano


def test_name_variants_and_relevance():
    assert set(rg.name_variants("NoxNano (Noxor)")) == {"NoxNano", "Noxor"}
    assert "Florida" not in rg.name_variants("RevivaRoof (Florida)")
    assert rg.is_test_entry("QA_Test_NanoRoof_Solutions")
    assert not rg.is_test_entry("Roof Maxx")
    assert not rg.mentions_competitor("Bright Green Roof", "bright green balcony planters on a peaked roof")


def test_brand_colours_still_present(monkeypatch):
    html = _build(monkeypatch, GOOD)["html"]
    for c in ("#1B1C36", "#675CE7", "#8583F2"):
        assert c in html
    assert "<script" not in html.lower()
