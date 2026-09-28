"""
youtube_tracker.py
Open-Source YouTube Competitive Intelligence Tracker.
Scrapes competitor videos, views, upload dates, thumbnails, and channel posts
using open endpoints and RSS feeds without requiring a paid YouTube API key.
"""
import json
import re
import urllib.parse
from typing import Dict, List, Any
import httpx
import feedparser

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}

def search_youtube_videos(query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Searches YouTube for videos related to a competitor or keyword without an API key
    by parsing YouTube's public search response.
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=CAI%253D"  # Sort by upload date
    
    videos = []
    try:
        response = httpx.get(url, headers=HEADERS, timeout=12.0, follow_redirects=True)
        if response.status_code == 200:
            html = response.text
            # Extract ytInitialData JSON object from script
            match = re.search(r"var ytInitialData\s*=\s*({.+?});</script>", html)
            if not match:
                match = re.search(r"window\[\"ytInitialData\"\]\s*=\s*({.+?});</script>", html)
                
            if match:
                data = json.loads(match.group(1))
                contents = (
                    data.get("contents", {})
                    .get("twoColumnSearchResultsRenderer", {})
                    .get("primaryContents", {})
                    .get("sectionListRenderer", {})
                    .get("contents", [])
                )
                
                for section in contents:
                    items = (
                        section.get("itemSectionRenderer", {})
                        .get("contents", [])
                    )
                    for item in items:
                        if "videoRenderer" in item:
                            vr = item["videoRenderer"]
                            video_id = vr.get("videoId")
                            title = vr.get("title", {}).get("runs", [{}])[0].get("text", "Untitled")
                            channel_name = vr.get("ownerText", {}).get("runs", [{}])[0].get("text", "Unknown Channel")
                            views_text = vr.get("viewCountText", {}).get("simpleText", "")
                            if not views_text and "runs" in vr.get("viewCountText", {}):
                                views_text = "".join([r.get("text", "") for r in vr["viewCountText"]["runs"]])
                            published_text = vr.get("publishedTimeText", {}).get("simpleText", "Recently")
                            desc_snippet = ""
                            if "detailedMetadataSnippets" in vr:
                                desc_snippet = vr["detailedMetadataSnippets"][0].get("snippetText", {}).get("runs", [{}])[0].get("text", "")
                            
                            thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                            if vr.get("thumbnail", {}).get("thumbnails"):
                                thumbnail_url = vr["thumbnail"]["thumbnails"][-1].get("url")

                            videos.append({
                                "source": "YouTube",
                                "id": video_id,
                                "title": title,
                                "channel": channel_name,
                                "published": published_text,
                                "views": views_text or "N/A",
                                "url": f"https://www.youtube.com/watch?v=/{video_id}",
                                "thumbnail": thumbnail_url,
                                "snippet": desc_snippet
                            })
                            if len(videos) >= limit:
                                break
                    if len(videos) >= limit:
                        break
    except Exception as e:
        print(f"Error scraping YouTube videos for {query}: {e}")

    # Fallback to YouTube RSS if web scraping is blocked or empty
    if not videos:
        videos = fetch_youtube_rss_fallback(query, limit=limit)

    return videos


def fetch_youtube_rss_fallback(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fallback video search via Google News video index.
    """
    encoded = urllib.parse.quote(f"site:youtube.com {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    results = []
    
    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        link = entry.get("link", "")
        video_id = ""
        if "watch?v=" in link:
            video_id = link.split("watch?v=")[-1].split("&")[0]
        
        results.append({
            "source": "YouTube",
            "id": video_id,
            "title": title,
            "channel": entry.get("source", {}).get("title", "YouTube"),
            "published": entry.get("published", "Recent"),
            "views": "Public Post",
            "url": link,
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "https://via.placeholder.com/320x180.png?text=YouTube+Video",
            "snippet": entry.get("summary", "")
        })
    return results


def fetch_channel_rss(channel_id: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Fetches latest videos directly from a YouTube Channel's public RSS feed.
    """
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(url)
    videos = []
    
    for entry in feed.entries[:limit]:
        video_id = entry.get("yt_videoid", "")
        videos.append({
            "source": "YouTube Channel",
            "id": video_id,
            "title": entry.get("title", ""),
            "channel": entry.get("author", "Competitor Channel"),
            "published": entry.get("published", "")[:10],
            "views": "Official Upload",
            "url": entry.get("link", f"https://www.youtube.com/watch?v={video_id}"),
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "snippet": entry.get("summary", "")[:250]
        })
    return videos
