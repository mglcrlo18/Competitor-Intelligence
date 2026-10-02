"""
auxiliary_sources.py
Diversified zero-cost data streams for the Competitor Intelligence Pipeline.

Implements the two remaining architectural pillars from the report:
  - GAP 8: Free-Tier News API Integration (GNews, NewsData.io, Currents, Mediastack)
  - GAP 9: RSSHub feed generation + Algolia Hacker News Search API

All APIs are used as *discovery endpoints* — article URLs are extracted and passed
through the existing pipeline_utils data-fidelity chain (curl_cffi → Trafilatura →
WAF detection → cache-aside → dedup) for full-text extraction.

Free-tier constraints navigated:
  - GNews:      100 requests/day, truncated content   → URL discovery only
  - NewsData:   200 credits/day,  partial content      → URL discovery only
  - Currents:   ~600 requests/day, basic categories    → URL discovery only
  - Mediastack: 100 requests/month, 12-24h delay      → URL discovery only
  - Algolia HN: No API key, no rate wall               → full integration
  - RSSHub:     Self-hosted, unlimited                  → feed URL construction
"""
import os
import urllib.parse
from typing import Any, Dict, List, Optional

import httpx
import feedparser

from pipeline_utils import (
    cache_lookup,
    cache_store,
    fetch_and_extract,
    fetch_rss_feed,
    is_near_duplicate,
    is_valid_article,
)

# ---------------------------------------------------------------------------
# API Keys — sourced from environment variables (zero-cost free tiers)
# ---------------------------------------------------------------------------
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")
MEDIASTACK_API_KEY = os.getenv("MEDIASTACK_API_KEY", "")

# Base timeout for all API calls
API_TIMEOUT = 12.0

# Default RSSHub instance — users can self-host on Vercel/Cloudflare Workers/Docker
# and override this via environment variable.
RSSHUB_BASE_URL = os.getenv("RSSHUB_BASE_URL", "https://rsshub.app")


# ---------------------------------------------------------------------------
# SHARED HELPERS
# ---------------------------------------------------------------------------
def _enrich_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches a discovery-only article dict by fetching full article text
    through the data-fidelity chain (curl_cffi + Trafilatura + WAF detection).
    Uses cache-aside to prevent redundant network calls.
    """
    url = article.get("link", "")
    if not url or url == "#":
        return article

    cached = cache_lookup(url)
    if cached:
        article["full_text"] = cached.get("article_text", "")
        return article

    full_text = fetch_and_extract(url, timeout=10.0)
    cache_store(url, url, article_text=full_text)
    article["full_text"] = full_text or ""
    return article


def _safe_api_get(url: str, params: Optional[Dict] = None,
                  headers: Optional[Dict] = None) -> Optional[Dict]:
    """Safe JSON GET with timeout and error handling."""
    try:
        resp = httpx.get(
            url,
            params=params,
            headers=headers or {},
            timeout=API_TIMEOUT,
            follow_redirects=True,
        )
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            print(f"[auxiliary_sources] Rate limited (429) on {url}")
        else:
            print(f"[auxiliary_sources] HTTP {resp.status_code} from {url}")
    except Exception as e:
        print(f"[auxiliary_sources] API call failed for {url}: {e}")
    return None


# ===================================================================
# GAP 8: FREE-TIER NEWS API INTEGRATION
# ===================================================================

# ---------------------------------------------------------------------------
# 8A. GNews API  (100 requests/day, truncated content)
# https://gnews.io/docs/v4
# ---------------------------------------------------------------------------
def fetch_gnews_articles(
    query: str,
    *,
    max_results: int = 10,
    lang: str = "en",
    country: str = "us",
    api_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Fetches articles from the GNews API free tier.
    Used strictly as a discovery endpoint — URLs are passed through the
    data-fidelity chain for full-text extraction.

    Free-tier limit: 100 requests/day, non-commercial use only.
    """
    key = api_key or GNEWS_API_KEY
    if not key:
        return []

    data = _safe_api_get(
        "https://gnews.io/api/v4/search",
        params={
            "q": query,
            "lang": lang,
            "country": country,
            "max": str(min(max_results, 10)),  # free tier max is 10
            "apikey": key,
        },
    )
    if not data:
        return []

    articles = []
    for item in data.get("articles", []):
        article = {
            "title": item.get("title", ""),
            "link": item.get("url", "#"),
            "summary": item.get("description", ""),
            "source": item.get("source", {}).get("name", "GNews"),
            "published": item.get("publishedAt", "Recent"),
            "api_source": "GNews",
            "full_text": "",
        }
        articles.append(_enrich_article(article))
    return articles


# ---------------------------------------------------------------------------
# 8B. NewsData.io  (200 credits/day, partial content)
# https://newsdata.io/documentation
# ---------------------------------------------------------------------------
def fetch_newsdata_articles(
    query: str,
    *,
    max_results: int = 10,
    lang: str = "en",
    country: str = "us",
    api_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Fetches articles from the NewsData.io API free tier.
    Free-tier limit: 200 credits/day. Each request = 1 credit.
    """
    key = api_key or NEWSDATA_API_KEY
    if not key:
        return []

    data = _safe_api_get(
        "https://newsdata.io/api/1/latest",
        params={
            "q": query,
            "language": lang,
            "country": country,
            "apikey": key,
        },
    )
    if not data or data.get("status") != "success":
        return []

    articles = []
    for item in data.get("results", [])[:max_results]:
        article = {
            "title": item.get("title", ""),
            "link": item.get("link", "#"),
            "summary": item.get("description", "") or item.get("content", ""),
            "source": item.get("source_name", "NewsData.io"),
            "published": item.get("pubDate", "Recent"),
            "api_source": "NewsData.io",
            "full_text": "",
        }
        articles.append(_enrich_article(article))
    return articles


# ---------------------------------------------------------------------------
# 8C. Currents API  (~600 requests/day)
# https://currentsapi.services/en/docs/
# ---------------------------------------------------------------------------
def fetch_currents_articles(
    query: str,
    *,
    max_results: int = 10,
    lang: str = "en",
    api_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Fetches articles from the Currents API free tier.
    Free-tier limit: ~600 requests/day. Allowed for commercial use.
    """
    key = api_key or CURRENTS_API_KEY
    if not key:
        return []

    data = _safe_api_get(
        "https://api.currentsapi.services/v1/search",
        params={
            "keywords": query,
            "language": lang,
            "apiKey": key,
        },
    )
    if not data or data.get("status") != "ok":
        return []

    articles = []
    for item in data.get("news", [])[:max_results]:
        article = {
            "title": item.get("title", ""),
            "link": item.get("url", "#"),
            "summary": item.get("description", ""),
            "source": item.get("author", "Currents"),
            "published": item.get("published", "Recent"),
            "api_source": "Currents",
            "full_text": "",
        }
        articles.append(_enrich_article(article))
    return articles


# ---------------------------------------------------------------------------
# 8D. Mediastack API  (100 requests/month, 12-24h delay)
# https://mediastack.com/documentation
# ---------------------------------------------------------------------------
def fetch_mediastack_articles(
    query: str,
    *,
    max_results: int = 10,
    languages: str = "en",
    api_key: str = "",
) -> List[Dict[str, Any]]:
    """
    Fetches articles from the Mediastack API free tier.
    Free-tier limit: 100 requests/month. Use sparingly.
    Note: Free tier requires HTTP (not HTTPS) on the base URL.
    """
    key = api_key or MEDIASTACK_API_KEY
    if not key:
        return []

    # Mediastack free tier does not support HTTPS — must use HTTP
    data = _safe_api_get(
        "http://api.mediastack.com/v1/news",
        params={
            "keywords": query,
            "languages": languages,
            "limit": str(min(max_results, 25)),
            "access_key": key,
        },
    )
    if not data:
        return []

    articles = []
    for item in data.get("data", [])[:max_results]:
        article = {
            "title": item.get("title", ""),
            "link": item.get("url", "#"),
            "summary": item.get("description", ""),
            "source": item.get("source", "Mediastack"),
            "published": item.get("published_at", "Recent"),
            "api_source": "Mediastack",
            "full_text": "",
        }
        articles.append(_enrich_article(article))
    return articles


# ---------------------------------------------------------------------------
# 8E. Aggregated Free-Tier API Discovery
# ---------------------------------------------------------------------------
def fetch_all_free_api_articles(
    query: str,
    *,
    max_per_source: int = 5,
) -> List[Dict[str, Any]]:
    """
    Queries all configured free-tier News APIs and returns a combined,
    deduplicated article list.  Only APIs with valid keys are queried.
    Articles are enriched with full-text extraction via the data-fidelity chain.
    """
    all_articles: List[Dict[str, Any]] = []

    # Query each API that has a configured key
    if GNEWS_API_KEY:
        all_articles.extend(fetch_gnews_articles(query, max_results=max_per_source))
    if NEWSDATA_API_KEY:
        all_articles.extend(fetch_newsdata_articles(query, max_results=max_per_source))
    if CURRENTS_API_KEY:
        all_articles.extend(fetch_currents_articles(query, max_results=max_per_source))
    if MEDIASTACK_API_KEY:
        all_articles.extend(fetch_mediastack_articles(query, max_results=max_per_source))

    # Deduplicate across sources using the existing MinHash pipeline
    deduplicated = []
    for art in all_articles:
        text = art.get("full_text") or art.get("summary") or art.get("title", "")
        doc_id = art.get("link", str(len(deduplicated)))
        if text and not is_near_duplicate(text, f"api_{doc_id}"):
            deduplicated.append(art)

    return deduplicated


# ===================================================================
# GAP 9: RSSHUB + ALGOLIA HACKER NEWS INTEGRATION
# ===================================================================

# ---------------------------------------------------------------------------
# 9A. Algolia Hacker News Search API  (No API key, no rate wall)
# https://hn.algolia.com/api
# ---------------------------------------------------------------------------
def fetch_hackernews_mentions(
    query: str,
    *,
    max_results: int = 15,
    tags: str = "story",
) -> List[Dict[str, Any]]:
    """
    Searches Hacker News via the Algolia Search API for brand mentions,
    product launches, and developer community sentiment.

    No API key required.  No documented rate limit.
    Supports tags: story, comment, show_hn, ask_hn, poll, front_page.
    """
    encoded_query = urllib.parse.quote(query.strip())
    data = _safe_api_get(
        "https://hn.algolia.com/api/v1/search",
        params={
            "query": query.strip(),
            "tags": tags,
            "hitsPerPage": str(min(max_results, 50)),
        },
    )
    if not data:
        return []

    mentions = []
    for hit in data.get("hits", [])[:max_results]:
        title = hit.get("title") or hit.get("story_title") or ""
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
        points = hit.get("points", 0)
        num_comments = hit.get("num_comments", 0)
        author = hit.get("author", "")
        created_at = hit.get("created_at", "Recent")

        # For HN stories with external URLs, fetch full text through the pipeline
        full_text = ""
        if hit.get("url"):
            cached = cache_lookup(url)
            if cached:
                full_text = cached.get("article_text", "")
            else:
                full_text = fetch_and_extract(url, timeout=10.0) or ""
                cache_store(url, url, article_text=full_text if full_text else None)

        mentions.append({
            "source": "Hacker News",
            "channel_badge": "[TECH] Hacker News",
            "author": author,
            "title": title,
            "snippet": hit.get("story_text") or hit.get("comment_text") or title,
            "full_text": full_text,
            "score": str(points),
            "comments": str(num_comments),
            "url": url,
            "timestamp": created_at,
            "hn_id": hit.get("objectID", ""),
        })
    return mentions


def fetch_hackernews_comments(
    query: str,
    *,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """
    Searches HN comments specifically for brand/product mentions
    to capture developer sentiment and technical discussions.
    """
    return fetch_hackernews_mentions(query, max_results=max_results, tags="comment")


# ---------------------------------------------------------------------------
# 9B. RSSHub Feed Integration
# ---------------------------------------------------------------------------
# Pre-configured RSSHub routes for competitor intelligence.
# Full route catalog: https://docs.rsshub.app/
RSSHUB_ROUTES = {
    # Social media monitoring
    "twitter_user": "/twitter/user/{handle}",
    "twitter_keyword": "/twitter/keyword/{keyword}",
    "youtube_channel": "/youtube/channel/{channel_id}",
    "youtube_keyword": "/youtube/keyword/{keyword}",
    "reddit_subreddit": "/reddit/subreddit/{subreddit}/hot",
    "reddit_search": "/reddit/search/{query}",
    # Tech & developer platforms
    "github_trending": "/github/trending/{language}/daily",
    "github_repos": "/github/repos/{owner}",
    "producthunt": "/producthunt/today",
    # Business & finance
    "google_news_topic": "/google/news/{topic}/{lang}",
    "wsj": "/wsj/{section}",
    "bloomberg": "/bloomberg",
    # Custom search
    "google_search": "/google/search?q={query}",
}


def build_rsshub_url(route_key: str, **params: str) -> str:
    """
    Constructs a full RSSHub URL from a route template and parameters.

    Example:
        build_rsshub_url("twitter_keyword", keyword="roof+rejuvenation")
        → "https://rsshub.app/twitter/keyword/roof+rejuvenation"
    """
    template = RSSHUB_ROUTES.get(route_key, "")
    if not template:
        return ""
    try:
        path = template.format(**params)
    except KeyError as e:
        print(f"[auxiliary_sources] Missing RSSHub parameter: {e}")
        return ""
    return f"{RSSHUB_BASE_URL}{path}"


def fetch_rsshub_feed(
    route_key: str,
    *,
    max_results: int = 15,
    **route_params: str,
) -> List[Dict[str, Any]]:
    """
    Fetches and parses an RSSHub-generated feed.

    RSSHub dynamically generates RSS feeds for 5,000+ websites that don't
    natively support RSS (Twitter, YouTube comments, GitHub, ProductHunt, etc.).

    Deployment options (all zero-cost):
      - Public instance: https://rsshub.app (default, rate-limited)
      - Self-hosted: Vercel, Cloudflare Workers, Docker on Oracle free tier

    Args:
        route_key: Key from RSSHUB_ROUTES (e.g., "twitter_keyword")
        max_results: Maximum number of items to return
        **route_params: Parameters to fill the route template

    Returns:
        List of article/mention dicts with full_text extraction.
    """
    url = build_rsshub_url(route_key, **route_params)
    if not url:
        return []

    rss_text = fetch_rss_feed(url, timeout=15.0)
    if not rss_text:
        return []

    feed = feedparser.parse(rss_text)
    items = []
    for entry in feed.entries[:max_results]:
        title = entry.get("title", "")
        link = entry.get("link", "#")
        summary = entry.get("summary", "")

        # Extract full text for news-type entries
        full_text = ""
        if link and link != "#" and not link.startswith(RSSHUB_BASE_URL):
            cached = cache_lookup(link)
            if cached:
                full_text = cached.get("article_text", "")
            else:
                full_text = fetch_and_extract(link, timeout=10.0) or ""
                cache_store(link, link, article_text=full_text if full_text else None)

        items.append({
            "source": f"RSSHub ({route_key})",
            "channel_badge": f"[RSSHUB] {route_key}",
            "author": entry.get("author", ""),
            "title": title,
            "snippet": summary or title,
            "full_text": full_text,
            "score": "N/A",
            "comments": "N/A",
            "url": link,
            "timestamp": entry.get("published", "Recent"),
        })
    return items


def fetch_rsshub_competitor_bundle(
    competitor_name: str,
    *,
    max_per_route: int = 5,
) -> List[Dict[str, Any]]:
    """
    Queries multiple RSSHub routes for a competitor name to capture mentions
    across social media, developer platforms, and niche aggregators.
    """
    all_items: List[Dict[str, Any]] = []
    keyword = urllib.parse.quote(competitor_name.strip())

    # Twitter keyword search
    items = fetch_rsshub_feed("twitter_keyword", max_results=max_per_route, keyword=keyword)
    all_items.extend(items)

    # YouTube keyword search
    items = fetch_rsshub_feed("youtube_keyword", max_results=max_per_route, keyword=keyword)
    all_items.extend(items)

    # Reddit search
    items = fetch_rsshub_feed("reddit_search", max_results=max_per_route, query=keyword)
    all_items.extend(items)

    return all_items


# ===================================================================
# UNIFIED AGGREGATOR
# ===================================================================
def fetch_all_auxiliary_signals(
    query: str,
    *,
    include_news_apis: bool = True,
    include_hackernews: bool = True,
    include_rsshub: bool = True,
    max_per_source: int = 5,
) -> List[Dict[str, Any]]:
    """
    Master aggregator for all auxiliary zero-cost data streams.
    Returns a deduplicated, enriched list of articles and mentions
    from free-tier News APIs, Hacker News, and RSSHub feeds.

    All results pass through the data-fidelity chain:
      curl_cffi → Trafilatura → WAF detection → cache-aside → MinHash dedup
    """
    all_items: List[Dict[str, Any]] = []

    if include_news_apis:
        all_items.extend(fetch_all_free_api_articles(query, max_per_source=max_per_source))

    if include_hackernews:
        all_items.extend(fetch_hackernews_mentions(query, max_results=max_per_source))

    if include_rsshub:
        all_items.extend(fetch_rsshub_competitor_bundle(query, max_per_route=max_per_source))

    # Final cross-source deduplication
    deduplicated = []
    for art in all_items:
        text = art.get("full_text") or art.get("snippet") or art.get("title", "")
        doc_id = art.get("url", str(len(deduplicated)))
        if text and not is_near_duplicate(text, f"aux_{doc_id}"):
            deduplicated.append(art)

    return deduplicated
