"""
news_signals.py
Tracks competitor press releases, product updates, and business decisions
using a two-tier verified URL architecture:
- Primary: Bing News RSS (returns direct publisher URLs with zero wrappers).
- Fallback: Google News RSS with automatic redirect resolution to eliminate 404 links.
"""
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx
import feedparser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
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

def _extract_direct_url_from_bing(link: str) -> str:
    """Extracts direct publisher URL from Bing redirect wrapper."""
    if not link:
        return "#"
    if "bing.com/news/apiclick" in link:
        try:
            parsed = urllib.parse.urlparse(link)
            qs = urllib.parse.parse_qs(parsed.query)
            if "url" in qs and qs["url"]:
                return qs["url"][0]
        except Exception:
            pass
    return link

def _resolve_google_redirect(url: str) -> str:
    """Follows Google News redirect wrappers to capture the real destination URL."""
    if not url or "news.google.com" not in url:
        return url
    try:
        r = httpx.head(url, headers=HEADERS, timeout=6.0, follow_redirects=True)
        final_url = str(r.url)
        if "news.google.com" not in final_url and final_url != url:
            return final_url
    except Exception:
        pass
    try:
        r = httpx.get(url, headers=HEADERS, timeout=6.0, follow_redirects=True)
        final_url = str(r.url)
        if "news.google.com" not in final_url and final_url != url:
            return final_url
    except Exception:
        pass
    return url

def _fetch_bing_news(query_str: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Fetches direct articles via Bing News RSS."""
    query = urllib.parse.quote(query_str.strip())
    rss_url = f"https://www.bing.com/news/search?q={query}&format=rss"
    
    try:
        response = httpx.get(rss_url, headers=HEADERS, timeout=10.0, follow_redirects=True)
        if response.status_code != 200 or not response.text:
            return []
            
        feed = feedparser.parse(response.text)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No Title")
            summary = entry.get("summary", "")
            raw_link = entry.get("link", "#")
            direct_link = _extract_direct_url_from_bing(raw_link)
            sig = score_article_significance(title, summary)
            
            results.append({
                "title": title,
                "link": direct_link,
                "published": entry.get("published", "Recent"),
                "source": entry.get("source", {}).get("title", "News Publication"),
                "summary": summary,
                "threat_level": sig["threat_tier"],
                "category": sig["primary_category"],
                "is_significant": sig["is_significant"],
                "score": sig["score"]
            })
        return results
    except Exception as e:
        print(f"Failed to fetch Bing News RSS for '{query_str}': {e}")
        return []

def _fetch_google_news_fallback(query_str: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Fallback Google News RSS with redirect resolution to avoid 404 links."""
    query = urllib.parse.quote(query_str.strip())
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = httpx.get(rss_url, headers=HEADERS, timeout=10.0, follow_redirects=True)
        if response.status_code != 200 or not response.text:
            return []
            
        feed = feedparser.parse(response.text)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No Title")
            summary = entry.get("summary", "")
            raw_link = entry.get("link", "#")
            resolved_link = _resolve_google_redirect(raw_link)
            sig = score_article_significance(title, summary)
            
            results.append({
                "title": title,
                "link": resolved_link,
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
    Fetches real-time verified news articles using Bing News primary and Google News fallback.
    """
    clean_name = company_name.strip()
    if not clean_name:
        clean_name = "Roof Rejuvenation"
        
    # 1. Primary: Direct query on Bing News
    articles = _fetch_bing_news(clean_name, limit=limit)
    if articles:
        return articles
        
    # 2. Contextual query on Bing News
    contextual_query = f"{clean_name} roof OR coating OR shingles"
    articles = _fetch_bing_news(contextual_query, limit=limit)
    if articles:
        return articles

    # 3. Fallback: Google News with redirect resolution
    articles = _fetch_google_news_fallback(clean_name, limit=limit)
    if articles:
        return articles
        
    # 4. Industry fallback
    fallback_query = "roof rejuvenation OR shingle restoration OR nano roof coating"
    articles = _fetch_bing_news(fallback_query, limit=limit)
    if not articles:
        articles = _fetch_google_news_fallback(fallback_query, limit=limit)
    for a in articles:
        a["is_industry_fallback"] = True
    return articles

def fetch_company_overview_headlines(company_name: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Fetches latest verified news headlines for the Executive Overview.
    """
    news = fetch_competitor_news(company_name, limit=limit)
    return news[:limit]
