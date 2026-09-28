"""
keyword_tracker.py
Tracks keyword interest and search demand using Google Trends (pytrends)
and provides quick SERP research links without paid APIs.
"""
import urllib.parse
from typing import Dict, List, Any
import pandas as pd


def get_serp_research_links(keyword: str, competitor_domain: str = "") -> Dict[str, str]:
    """
    Generates instant zero-cost SERP check queries across search engines.
    """
    kw_encoded = urllib.parse.quote(keyword)
    domain_encoded = urllib.parse.quote(f"site:{competitor_domain} {keyword}") if competitor_domain else kw_encoded
    
    return {
        "Google SERP": f"https://www.google.com/search?q={kw_encoded}",
        "Competitor Indexed Pages (Google)": f"https://www.google.com/search?q={domain_encoded}",
        "DuckDuckGo Search": f"https://duckduckgo.com/?q={kw_encoded}",
        "Bing Search": f"https://www.bing.com/search?q={kw_encoded}"
    }


def fetch_google_trends(keywords: List[str], timeframe: str = "today 12-m", geo: str = "") -> Optional[pd.DataFrame]:
    """
    Fetches relative search interest over time across target keywords or competitors (100% free).
    """
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl="en-US", tz=360)
        # Max 5 keywords per request allowed by Google Trends
        kw_list = keywords[:5]
        pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo)
        interest_df = pytrends.interest_over_time()
        if not interest_df.empty and "isPartial" in interest_df.columns:
            interest_df = interest_df.drop(columns=["isPartial"])
        return interest_df
    except Exception as e:
        print(f"Error fetching Google Trends: {e}")
        return None
