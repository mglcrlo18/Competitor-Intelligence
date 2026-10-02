"""
osint_listener.py
Open-Source Social & Web Listening Engine.
Scrapes competitor mentions and community sentiment across real Reddit and Forums
using DuckDuckGo HTML fallbacks to avoid IP bans, and Google News RSS for official PR.
"""
import urllib.parse
from typing import Dict, List, Any
import httpx
from bs4 import BeautifulSoup
import feedparser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

def fetch_reddit_mentions(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Fetches genuine Reddit mentions using DuckDuckGo Lite.
    Removes faked engagement metrics.
    """
    clean_query = query.strip()
    if not clean_query:
        clean_query = "roof rejuvenation"
        
    mentions = []
    
    # 1. Fetch community reviews and discussions via DuckDuckGo Lite
    ddg_query = urllib.parse.quote(f"site:reddit.com {clean_query}")
    url = f"https://lite.duckduckgo.com/lite/"
    
    try:
        res = httpx.post(url, data={"q": f"site:reddit.com {clean_query}"}, headers=HEADERS, timeout=12.0)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for tr in soup.find_all("tr"):
                td = tr.find("td", class_="result-snippet")
                if td:
                    title_a = tr.previous_sibling.find("a", class_="result-url") if tr.previous_sibling else None
                    if title_a:
                        raw_href = title_a["href"]
                        # Decode the URL to properly check if it contains reddit.com
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
                                "score": "N/A",  # Real metric requires Reddit API
                                "comments": "N/A",
                                "url": real_url,
                                "timestamp": "Recent"
                            })
                            if len(mentions) >= limit:
                                break
    except Exception as e:
        print(f"Error fetching real Reddit mentions for '{query}': {e}")

    return mentions

def _fetch_rss(query_str: str, limit: int = 15) -> List[Dict[str, Any]]:
    query = urllib.parse.quote(query_str.strip())
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        r = httpx.get(url, headers=HEADERS, timeout=10.0, follow_redirects=True)
        if r.status_code == 200 and r.text:
            feed = feedparser.parse(r.text)
            items = []
            for entry in feed.entries[:limit]:
                items.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", "#"),
                    "source": entry.get("source", {}).get("title", "News Outlet"),
                    "published": entry.get("published", "Recent")
                })
            return items
    except Exception as e:
        print(f"Error fetching RSS for '{query_str}': {e}")
    return []

def fetch_web_and_news_signals(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Fetches real news signals via Google News RSS.
    """
    raw = _fetch_rss(query, limit=limit)
    mentions = []
    for entry in raw:
        mentions.append({
            "source": entry["source"],
            "channel_badge": "[NEWS] Article",
            "author": entry["source"],
            "title": entry["title"],
            "snippet": entry["summary"] or entry["title"],
            "score": "N/A",
            "comments": "N/A",
            "url": entry["link"],
            "timestamp": entry["published"]
        })
    return mentions

def fetch_all_open_source_stream(competitor_name: str, limit_per_source: int = 10) -> List[Dict[str, Any]]:
    return fetch_reddit_mentions(competitor_name, limit=limit_per_source)
