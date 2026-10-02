"""
news_signals.py
Tracks competitor press releases, product updates, and business decisions
using a two-tier verified URL architecture:
- Primary: Bing News RSS (returns direct publisher URLs with zero wrappers).
- Fallback: Google News RSS with batchexecute RPC resolution via googlenewsdecoder.

Data-fidelity features (via pipeline_utils):
  - TLS-impersonated fetching (curl_cffi) to bypass WAF/JA3 fingerprinting.
  - Trafilatura content extraction for full article body text.
  - WAF challenge page detection to prevent poison data ingestion.
  - SQLite TTL cache-aside to prevent redundant network calls.
  - MinHash LSH near-duplicate detection to filter syndicated copies.
"""
import urllib.parse
from typing import List, Dict, Any, Optional
import feedparser

from pipeline_utils import (
    fetch_rss_feed,
    fetch_and_extract,
    resolve_google_news_url,
    is_near_duplicate,
    init_dedup_index,
    cache_lookup,
    cache_store,
    cache_evict_expired,
    is_valid_article,
)

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

def _fetch_bing_news(query_str: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Fetches direct articles via Bing News RSS with optimized parameters."""
    query = urllib.parse.quote(query_str.strip())
    # Advanced Bing RSS parameters: count=100 maximizes payload, freshness=Day for delta updates
    rss_url = f"https://www.bing.com/news/search?q={query}&format=rss&count=100&freshness=Day"
    
    try:
        rss_text = fetch_rss_feed(rss_url)
        if not rss_text:
            return []
        
        feed = feedparser.parse(rss_text)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No Title")
            summary = entry.get("summary", "")
            raw_link = entry.get("link", "#")
            direct_link = _extract_direct_url_from_bing(raw_link)
            
            # Cache-aside: check if we already have this article
            cached = cache_lookup(direct_link)
            if cached:
                full_text = cached.get("article_text", "")
            else:
                # Fetch full article text via TLS-impersonated curl_cffi + Trafilatura
                full_text = fetch_and_extract(direct_link, timeout=10.0)
                # Cache the result for future poll cycles
                cache_store(direct_link, direct_link, article_text=full_text)
            
            # Use full text for dedup, fall back to title+summary
            dedup_text = full_text if full_text else f"{title} {summary}"
            
            # Skip articles that fail validation (too short, WAF pages, etc.)
            if not is_valid_article(dedup_text) and not summary:
                continue
            
            # Near-duplicate detection: skip syndicated copies
            if is_near_duplicate(dedup_text, direct_link):
                continue
            
            sig = score_article_significance(title, summary)
            
            source_obj = entry.get("source")
            source_title = source_obj.get("title", "News Publication") if isinstance(source_obj, dict) else "News Publication"
            
            results.append({
                "title": title,
                "link": direct_link,
                "published": entry.get("published", "Recent"),
                "source": source_title,
                "summary": summary,
                "threat_level": sig["threat_tier"],
                "category": sig["primary_category"],
                "is_significant": sig["is_significant"],
                "score": sig["score"],
                "full_text": full_text or "",
            })
        return results
    except Exception as e:
        print(f"Failed to fetch Bing News RSS for '{query_str}': {e}")
        return []

def _fetch_google_news_fallback(query_str: str, limit: int = 25) -> List[Dict[str, Any]]:
    """Fallback Google News RSS with batchexecute RPC URL resolution via googlenewsdecoder."""
    query = urllib.parse.quote(query_str.strip())
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        rss_text = fetch_rss_feed(rss_url)
        if not rss_text:
            return []
        
        feed = feedparser.parse(rss_text)
        results = []
        for entry in feed.entries[:limit]:
            title = entry.get("title", "No Title")
            summary = entry.get("summary", "")
            raw_link = entry.get("link", "#")
            
            # Cache-aside: check if this opaque URL was already resolved
            cached = cache_lookup(raw_link)
            if cached:
                resolved_link = cached.get("resolved_url", raw_link)
                full_text = cached.get("article_text", "")
            else:
                # Resolve opaque Google News URL via batchexecute RPC
                resolved_link = resolve_google_news_url(raw_link)
                
                # Fetch full article text from the resolved publisher URL
                full_text = fetch_and_extract(resolved_link, timeout=10.0) if resolved_link != raw_link else None
                
                # Cache both the resolution and the extracted text
                cache_store(raw_link, resolved_link, article_text=full_text)
            
            # Use full text for dedup, fall back to title+summary
            dedup_text = full_text if full_text else f"{title} {summary}"
            
            if not is_valid_article(dedup_text) and not summary:
                continue
            
            if is_near_duplicate(dedup_text, resolved_link):
                continue
            
            sig = score_article_significance(title, summary)
            
            source_obj = entry.get("source")
            source_title = source_obj.get("title", "Google News") if isinstance(source_obj, dict) else "Google News"
            
            results.append({
                "title": title,
                "link": resolved_link,
                "published": entry.get("published", "Recent"),
                "source": source_title,
                "summary": summary,
                "threat_level": sig["threat_tier"],
                "category": sig["primary_category"],
                "is_significant": sig["is_significant"],
                "score": sig["score"],
                "full_text": full_text or "",
            })
        return results
    except Exception as e:
        print(f"Failed to fetch Google News RSS for '{query_str}': {e}")
        return []

def fetch_competitor_news(company_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetches real-time verified news articles using Bing News primary and Google News fallback.
    Includes full-text extraction, cache-aside, deduplication, and WAF detection.
    """
    # Evict expired cache entries once per poll cycle
    cache_evict_expired()
    # Reset the dedup index for this poll cycle
    init_dedup_index()
    
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

    # 3. Fallback: Google News with batchexecute resolution
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
