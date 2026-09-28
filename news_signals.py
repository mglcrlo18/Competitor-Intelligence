"""
news_signals.py
Tracks competitor press releases, product updates, and business decisions
using Google News RSS feeds fetched via HTTPX (bypassing macOS Python urllib SSL cert errors).
"""
import urllib.parse
from typing import List, Dict, Any
import httpx
import feedparser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*"
}

SIGNIFICANT_KEYWORDS = {
    "Expansion & Territory": ["expansion", "expand", "territory", "dealer", "franchise", "new location", "market entry"],
    "Product & Formula": ["patent", "launch", "breakthrough", "nanotechnology", "bio-oil", "coating", "rejuvenation", "formula", "innovation", "shingle"],
    "Warranty & Pricing": ["warranty", "guarantee", "cost", "price", "discount", "financing", "insurance"],
    "Partnership & M&A": ["partnership", "acquisition", "acquire", "merger", "partner", "joint venture", "distributor"],
    "Regulatory & Standards": ["code", "compliance", "standard", "certified", "lawsuit", "investigation", "safety"]
}

def score_article_significance(title: str, summary: str) -> Dict[str, Any]:
    text = (title + " " + summary).lower()
    matched_categories = []
    score = 1
    
    for category, keywords in SIGNIFICANT_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched_categories.append(category)
                score += 2
                break
                
    threat_tier = "Moderate"
    if score >= 5:
        threat_tier = "High"
    elif score <= 2:
        threat_tier = "Low"
        
    primary_category = matched_categories[0] if matched_categories else "Company Update"
    return {
        "score": score,
        "threat_tier": threat_tier,
        "primary_category": primary_category,
        "is_significant": score >= 2
    }

def _fetch_rss_via_httpx(query_str: str, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Fetches Google News RSS content via HTTPX to ensure valid SSL certificates,
    then parses the raw XML string with feedparser.
    """
    query = urllib.parse.quote(query_str.strip())
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = httpx.get(rss_url, headers=HEADERS, timeout=12.0, follow_redirects=True)
        if response.status_code != 200 or not response.text:
            return []
            
        feed = feedparser.parse(response.text)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No Title")
            summary = entry.get("summary", "")
            sig = score_article_significance(title, summary)
            
            results.append({
                "title": title,
                "link": entry.get("link", "#"),
                "published": entry.get("published", "Recent"),
                "source": entry.get("source", {}).get("title", "Google News"),
                "summary": summary,
                "threat_level": sig["threat_tier"],
                "category": sig["primary_category"],
                "is_significant": sig["is_significant"],
                "score": sig["score"]
            })
        return results
    except Exception as e:
        print(f"Failed to fetch Google News RSS for '{query_str}': {e}")
        return []

def fetch_competitor_news(company_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetches real-time indexed news for any company or keyword.
    Tries direct query first, then contextual fallback.
    """
    clean_name = company_name.strip()
    if not clean_name:
        clean_name = "Roof Rejuvenation"
        
    # 1. Direct query
    articles = _fetch_rss_via_httpx(clean_name, limit=limit)
    if articles:
        return articles
        
    # 2. Contextual query
    contextual_query = f"{clean_name} roof OR coating OR shingles"
    articles = _fetch_rss_via_httpx(contextual_query, limit=limit)
    if articles:
        return articles
        
    # 3. Industry fallback if ultra-niche
    fallback_query = "roof rejuvenation OR shingle restoration OR nano roof coating"
    articles = _fetch_rss_via_httpx(fallback_query, limit=limit)
    for a in articles:
        a["is_industry_fallback"] = True
    return articles

def fetch_company_overview_headlines(company_name: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Fetches all latest news headlines about the company for the Executive Overview.
    """
    news = fetch_competitor_news(company_name, limit=limit)
    return news[:limit]
