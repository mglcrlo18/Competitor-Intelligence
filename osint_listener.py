"""
osint_listener.py
Open-Source Social & Web Listening Engine.
Scrapes competitor mentions and community sentiment across real Reddit and Forums
using DuckDuckGo HTML fallbacks to avoid IP bans, and a two-tier news architecture:
- Primary: Bing News RSS for direct publisher article URLs without wrappers.
- Fallback: Google News RSS with batchexecute RPC resolution via googlenewsdecoder.

Data-fidelity features (via pipeline_utils):
  - TLS-impersonated fetching (curl_cffi) to bypass WAF/JA3 fingerprinting.
  - Trafilatura content extraction for full article body text.
  - WAF challenge page detection to prevent poison data ingestion.
  - SQLite TTL cache-aside to prevent redundant network calls.
  - MinHash LSH near-duplicate detection to filter syndicated copies.
"""
import urllib.parse
from typing import Dict, List, Any, Optional
import httpx
from bs4 import BeautifulSoup
import feedparser

from pipeline_utils import (
    fetch_rss_feed,
    fetch_and_extract,
    resolve_google_news_url,
    is_waf_challenge,
    is_near_duplicate,
    init_dedup_index,
    cache_lookup,
    cache_store,
    is_valid_article,
    BROWSER_HEADERS,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*"
}

def fetch_reddit_mentions(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Fetches genuine Reddit mentions using DuckDuckGo Lite.
    Removes faked engagement metrics.
    Uses WAF challenge detection to prevent ingesting bot-check pages.
    """
    clean_query = query.strip()
    if not clean_query:
        clean_query = "roof rejuvenation"
        
    mentions = []
    
    # Fetch community reviews and discussions via DuckDuckGo Lite
    url = "https://lite.duckduckgo.com/lite/"
    
    try:
        res = httpx.post(url, data={"q": f"site:reddit.com {clean_query}"}, headers=HEADERS, timeout=12.0)
        if res.status_code == 200 and not is_waf_challenge(res.text):
            soup = BeautifulSoup(res.text, "html.parser")
            for tr in soup.find_all("tr"):
                td = tr.find("td", class_="result-snippet")
                if td:
                    title_a = tr.previous_sibling.find("a", class_="result-url") if tr.previous_sibling else None
                    if title_a:
                        raw_href = title_a.get("href", "")
                        decoded_href = urllib.parse.unquote(raw_href)
                        if "reddit.com" in decoded_href.lower():
                            real_url = raw_href
                            if "uddg=" in raw_href:
                                parsed = urllib.parse.urlparse(raw_href)
                                params = urllib.parse.parse_qs(parsed.query)
                                if "uddg" in params:
                                    real_url = urllib.parse.unquote(params["uddg"][0])
                            
                            mentions.append({
                                "source": "Reddit",
                                "channel_badge": "[COMMUNITY] Reddit",
                                "author": "Reddit User",
                                "title": title_a.text.strip(),
                                "snippet": td.text.strip(),
                                "score": "N/A",
                                "comments": "N/A",
                                "url": real_url,
                                "timestamp": "Recent"
                            })
                            if len(mentions) >= limit:
                                break
    except Exception as e:
        print(f"Error fetching real Reddit mentions for '{query}': {e}")

    return mentions

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

def _fetch_bing_rss(query_str: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Fetches articles via Bing News RSS with optimized parameters."""
    query = urllib.parse.quote(query_str.strip())
    # Advanced Bing RSS parameters: count=100 maximizes payload, freshness=Day for delta updates
    url = f"https://www.bing.com/news/search?q={query}&format=rss&count=100&freshness=Day"
    try:
        rss_text = fetch_rss_feed(url, timeout=10.0)
        if not rss_text:
            return []
        feed = feedparser.parse(rss_text)
        items = []
        for entry in feed.entries[:limit]:
            raw_link = entry.get("link", "#")
            direct_link = _extract_direct_url_from_bing(raw_link)
            
            # Cache-aside: check if we already have this article
            cached = cache_lookup(direct_link)
            if cached:
                items.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": cached.get("resolved_url", direct_link),
                    "source": entry.get("source", {}).get("title", "News Publication"),
                    "published": entry.get("published", "Recent"),
                    "full_text": cached.get("article_text", ""),
                })
                continue
            
            # Fetch full article text via TLS-impersonated curl_cffi + Trafilatura
            full_text = fetch_and_extract(direct_link, timeout=10.0)
            
            # Cache the result for future poll cycles
            cache_store(direct_link, direct_link, article_text=full_text)
            
            items.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": direct_link,
                "source": entry.get("source", {}).get("title", "News Publication"),
                "published": entry.get("published", "Recent"),
                "full_text": full_text or "",
            })
        return items
    except Exception as e:
        print(f"Error fetching Bing RSS for '{query_str}': {e}")
    return []

def _fetch_google_rss_fallback(query_str: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Google News RSS fallback with batchexecute RPC URL resolution."""
    query = urllib.parse.quote(query_str.strip())
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    try:
        rss_text = fetch_rss_feed(url, timeout=10.0)
        if not rss_text:
            return []
        feed = feedparser.parse(rss_text)
        items = []
        for entry in feed.entries[:limit]:
            raw_link = entry.get("link", "#")
            
            # Cache-aside: check if this opaque URL was already resolved
            cached = cache_lookup(raw_link)
            if cached:
                items.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": cached.get("resolved_url", raw_link),
                    "source": entry.get("source", {}).get("title", "News Outlet"),
                    "published": entry.get("published", "Recent"),
                    "full_text": cached.get("article_text", ""),
                })
                continue
            
            # Resolve opaque Google News URL via batchexecute RPC
            resolved_link = resolve_google_news_url(raw_link)
            
            # Fetch full article text
            full_text = fetch_and_extract(resolved_link, timeout=10.0) if resolved_link != raw_link else None
            
            # Cache the resolution + extracted text
            cache_store(raw_link, resolved_link, article_text=full_text)
            
            items.append({
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "link": resolved_link,
                "source": entry.get("source", {}).get("title", "News Outlet"),
                "published": entry.get("published", "Recent"),
                "full_text": full_text or "",
            })
        return items
    except Exception as e:
        print(f"Error fetching Google RSS fallback for '{query_str}': {e}")
    return []

def fetch_web_and_news_signals(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Fetches real news signals via Bing News RSS primary and Google News fallback.
    Includes full-text extraction, cache-aside, and WAF detection.
    """
    # 1. Primary: Bing News
    raw = _fetch_bing_rss(query, limit=limit)
    if not raw:
        # 2. Contextual Bing query
        raw = _fetch_bing_rss(f"{query} roof", limit=limit)
    if not raw:
        # 3. Fallback: Google News with batchexecute resolution
        raw = _fetch_google_rss_fallback(query, limit=limit)

    mentions = []
    for entry in raw:
        # Build dedup text from full article or fallback to title+snippet
        dedup_text = entry.get("full_text") or (entry["title"] + " " + (entry.get("summary") or ""))
        doc_id = entry.get("link", str(len(mentions)))
        
        # Near-duplicate detection: skip syndicated copies
        if is_near_duplicate(dedup_text, doc_id):
            continue
        
        mentions.append({
            "source": entry["source"],
            "channel_badge": "[NEWS] Article",
            "author": entry["source"],
            "title": entry["title"],
            "snippet": entry.get("summary") or entry["title"],
            "full_text": entry.get("full_text", ""),
            "score": "N/A",
            "comments": "N/A",
            "url": entry["link"],
            "timestamp": entry["published"]
        })
    return mentions

from auxiliary_sources import fetch_all_auxiliary_signals

def fetch_all_open_source_stream(competitor_name: str, limit_per_source: int = 10) -> List[Dict[str, Any]]:
    """
    Aggregates Reddit community mentions, news signals, and auxiliary streams 
    (Free-tier APIs, Hacker News, RSSHub) into a unified list.
    Initializes the dedup index to filter near-duplicates across all sources.
    """
    # Reset dedup index for this poll cycle
    init_dedup_index()
    
    reddit = fetch_reddit_mentions(competitor_name, limit=limit_per_source)
    news = fetch_web_and_news_signals(competitor_name, limit=limit_per_source)
    
    # 3. Auxiliary Data Streams (Free-Tier News APIs, Hacker News, RSSHub)
    auxiliary = fetch_all_auxiliary_signals(competitor_name, max_per_source=limit_per_source)
    
    return reddit + news + auxiliary
