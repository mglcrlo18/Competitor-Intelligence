"""
ads_tracker.py
Tracks competitor active advertisements across Meta, Google, and LinkedIn.
Supports Meta Ad Library Graph API via search_terms (brand name) or page_id.
"""
import urllib.parse
from typing import Dict, List, Any, Optional
import httpx


def get_public_ad_transparency_links(company_name: Optional[str] = None, domain: str = "") -> Dict[str, str]:
    """
    Generates direct zero-cost URLs to inspect competitor ads in real-time
    on official public transparency libraries without requiring paid scrapers.
    """
    if not company_name or not str(company_name).strip():
        company_name = "GoNano"
    company_name = str(company_name).strip()
    encoded_name = urllib.parse.quote(company_name)
    encoded_domain = urllib.parse.quote(domain) if domain else encoded_name
    
    return {
        "Meta Ad Library (Facebook & Instagram)": (
            f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=ALL&q={encoded_name}"
        ),
        "Google Ads Transparency Center": (
            f"https://adstransparency.google.com/?region=anywhere&domain={encoded_domain}"
        ),
        "LinkedIn Ad Library": (
            f"https://www.linkedin.com/ad-library/search?keywords={encoded_name}"
        ),
        "TikTok Commercial Content Library": (
            f"https://library.tiktok.com/ads?region=all&adv_name={encoded_name}"
        )
    }


def lookup_facebook_page_id(query: str, access_token: str) -> Optional[Dict[str, str]]:
    """
    Looks up a Facebook Page ID using its username/handle or search query via Meta Graph API.
    """
    if not access_token or not query:
        return None
    
    # Clean username if full URL was pasted
    clean_query = query.strip().rstrip("/").split("/")[-1].replace("@", "")
    
    # 1. Try direct object lookup (works if clean_query is the exact page username/slug)
    url = f"https://graph.facebook.com/v20.0/{clean_query}"
    params = {"access_token": access_token, "fields": "id,name,link"}
    try:
        res = httpx.get(url, params=params, timeout=8.0)
        if res.status_code == 200:
            data = res.json()
            if "id" in data:
                return {"id": data["id"], "name": data.get("name", clean_query)}
    except Exception:
        pass
        
    # 2. Try pages search endpoint
    search_url = "https://graph.facebook.com/v20.0/pages/search"
    search_params = {"q": query, "fields": "id,name,link", "access_token": access_token, "limit": 1}
    try:
        res = httpx.get(search_url, params=search_params, timeout=8.0)
        if res.status_code == 200:
            data = res.json()
            items = data.get("data", [])
            if items:
                return {"id": items[0]["id"], "name": items[0].get("name", query)}
    except Exception:
        pass

    return None


def fetch_meta_ad_library_api(
    access_token: str,
    search_terms: str = "",
    page_id: str = "",
    countries: Optional[List[str]] = None,
    limit: int = 15
) -> Dict[str, Any]:
    """
    Fetches active ads using Meta's official Ad Library API.
    Does NOT require a Page ID! Can query purely by `search_terms` (company name).
    """
    if not access_token:
        return {"error": "Missing access token", "ads": []}
    
    if not search_terms and not page_id:
        return {"error": "Please provide a company name (search_terms) or a Page ID", "ads": []}

    target_countries = countries or ["US", "CA", "PH", "GB", "AU"]
    country_param = str(target_countries)
    
    url = "https://graph.facebook.com/v20.0/ads_archive"
    params = {
        "access_token": access_token,
        "ad_active_status": "ACTIVE",
        "ad_reached_countries": country_param,
        "fields": "id,ad_creation_time,ad_creative_bodies,ad_creative_link_captions,ad_creative_link_titles,ad_snapshot_url,page_name,page_id",
        "limit": limit
    }
    
    if page_id.strip():
        params["search_page_ids"] = page_id.strip()
    else:
        params["search_terms"] = search_terms.strip()
        
    try:
        response = httpx.get(url, params=params, timeout=15.0)
        if response.status_code == 200:
            data = response.json()
            ads = []
            for ad in data.get("data", []):
                bodies = ad.get("ad_creative_bodies", [])
                titles = ad.get("ad_creative_link_titles", [])
                ads.append({
                    "ad_id": ad.get("id"),
                    "page_name": ad.get("page_name", "Unknown Page"),
                    "page_id": ad.get("page_id", ""),
                    "created_time": ad.get("ad_creation_time"),
                    "body": bodies[0] if bodies else "No copy provided",
                    "link_title": titles[0] if titles else "",
                    "snapshot_url": ad.get("ad_snapshot_url")
                })
            return {"error": None, "ads": ads}
        else:
            err_msg = response.json().get("error", {}).get("message", response.text)
            return {"error": f"Meta API Error ({response.status_code}): {err_msg}", "ads": []}
    except Exception as e:
        return {"error": f"Request exception: {str(e)}", "ads": []}
