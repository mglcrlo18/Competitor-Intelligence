"""
daily_monitor.py
Automated 24-hour competitor intelligence runner.
Gathers news, hiring, and ad signals across all key competitors merged from Google Sheets.
"""
import json
import os
from datetime import datetime
from news_signals import fetch_competitor_news
from ads_tracker import get_public_ad_transparency_links
from db_manager import get_all_monitored_competitors

DEFAULT_COMPETITORS = [
    {"name": "RoofLife Canada", "domain": "rooflifecanada.com"},
    {"name": "Nasiol", "domain": "nasiol.com"},
    {"name": "Reviva Roof", "domain": "revivaroof.com"},
    {"name": "Spray-Net", "domain": "spray-net.com"},
    {"name": "ArmoveX", "domain": "armovex.com"},
    {"name": "Zinox Coating", "domain": "zinoxcoating.com"},
    {"name": "Roof Maxx", "domain": "roofmaxx.com"},
    {"name": "Sure Roof Pros", "domain": "sureroofpros.com"},
    {"name": "Ever Roof", "domain": "everroof.com"},
    {"name": "OnYa Roof", "domain": "onyaroof.com"}
]

def get_competitor_roster():
    try:
        comps = get_all_monitored_competitors()
        return comps if comps else DEFAULT_COMPETITORS
    except Exception:
        return DEFAULT_COMPETITORS

def run_daily_scan():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    competitors = get_competitor_roster()
    print(f"[{timestamp}] Starting 24-hour competitor intelligence scan for {len(competitors)} entities...")
    
    findings = []
    
    for comp in competitors[:15]: # Scan prioritized active batch
        name = comp["name"]
        domain = comp.get("domain", f"{name.lower().replace(' ', '')}.com")
        print(f"Scanning {name} ({domain})...")
        
        # 1. Fetch recent news
        news = fetch_competitor_news(name, limit=3)
        
        # 2. Ad transparency portals
        ad_links = get_public_ad_transparency_links(name, domain)
        
        findings.append({
            "timestamp": timestamp,
            "competitor": name,
            "domain": domain,
            "recent_news_count": len(news),
            "top_news": news[:2],
            "ad_portals": ad_links
        })
        
    output_path = os.path.join(os.path.dirname(__file__), "daily_digest.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
        
    print(f"[{timestamp}] Scan complete! Results saved to {output_path}")
    return findings

if __name__ == "__main__":
    run_daily_scan()
