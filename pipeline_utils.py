"""
pipeline_utils.py
Shared zero-cost data-fidelity utilities for the Competitor Intelligence Pipeline.

Implements the four critical pillars prescribed by the architecture report:
  1. WAF Challenge Detection — prevent poison data from entering the LLM pipeline.
  2. TLS-Impersonated Fetching — bypass JA3/JA4 fingerprint-based WAFs via curl_cffi.
  3. Content Extraction — Trafilatura-based boilerplate removal (F1=0.937).
  4. Google News URL Resolution — batchexecute RPC via googlenewsdecoder.
  5. MinHash LSH Near-Duplicate Detection — sub-linear deduplication.
  6. SQLite TTL Cache-Aside — prevent redundant network calls with jittered expiry.
"""
import hashlib
import json
import os
import random
import re
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Conditional imports — degrade gracefully if a dependency is not yet installed
# ---------------------------------------------------------------------------
try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

try:
    from googlenewsdecoder import new_decoderv1 as decode_google_news_url
    HAS_GNEWS_DECODER = True
except ImportError:
    HAS_GNEWS_DECODER = False

try:
    from datasketch import MinHash, MinHashLSH
    HAS_DATASKETCH = True
except ImportError:
    HAS_DATASKETCH = False

import httpx  # always available — baseline fallback

# ---------------------------------------------------------------------------
# 1. WAF CHALLENGE DETECTION
# ---------------------------------------------------------------------------
# Known WAF / bot-challenge page signatures that must never enter the LLM pipeline.
WAF_SIGNATURES = [
    "just a moment",
    "checking your browser",
    "enable javascript",
    "cloudflare",
    "attention required",
    "access denied",
    "please verify you are a human",
    "ray id:",
    "cf-browser-verification",
    "challenge-platform",
    "managed by akamai",
    "datadome",
    "incapsula",
    "imperva",
    "please turn javascript on",
    "security check",
    "bot protection",
    "_cf_chl_opt",
    "cf-chl-bypass",
    "consent.google.com",
]

# Minimum plausible article body length (characters).  Anything shorter
# after extraction is almost certainly a stub, error page, or paywall gate.
MIN_ARTICLE_LENGTH = 120


def is_waf_challenge(html: str) -> bool:
    """
    Returns True if the HTML body matches known WAF / bot-challenge page
    signatures, indicating that the response is NOT real article content.
    """
    if not html:
        return True
    lower = html[:4000].lower()  # only inspect the head — faster
    matches = sum(1 for sig in WAF_SIGNATURES if sig in lower)
    # A single generic word match can be a false positive; require ≥2
    # signatures OR a single highly-specific one.
    highly_specific = ["_cf_chl_opt", "cf-chl-bypass", "challenge-platform",
                       "cf-browser-verification", "consent.google.com"]
    if any(s in lower for s in highly_specific):
        return True
    return matches >= 2


def is_valid_article(text: Optional[str]) -> bool:
    """
    Returns True if extracted text looks like a genuine article body.
    """
    if not text:
        return False
    stripped = text.strip()
    if len(stripped) < MIN_ARTICLE_LENGTH:
        return False
    if is_waf_challenge(stripped):
        return False
    return True


# ---------------------------------------------------------------------------
# 2. TLS-IMPERSONATED FETCHING
# ---------------------------------------------------------------------------
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

RSS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def fetch_with_tls_impersonation(
    url: str,
    *,
    timeout: float = 12.0,
    impersonate: str = "chrome",
    headers: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """
    Fetches a URL using curl_cffi with TLS/JA3 fingerprint impersonation.
    Falls back to httpx if curl_cffi is not installed.

    Returns the response body text, or None on failure / WAF block.
    """
    merged_headers = {**BROWSER_HEADERS, **(headers or {})}

    # --- Primary: curl_cffi with TLS impersonation ---
    if HAS_CURL_CFFI:
        try:
            resp = cffi_requests.get(
                url,
                headers=merged_headers,
                timeout=timeout,
                impersonate=impersonate,
                allow_redirects=True,
            )
            if resp.status_code == 200 and resp.text:
                if not is_waf_challenge(resp.text):
                    return resp.text
                # WAF detected — try alternate browser fingerprint
                for alt in ("safari_ios", "firefox"):
                    if alt == impersonate:
                        continue
                    try:
                        resp2 = cffi_requests.get(
                            url,
                            headers=merged_headers,
                            timeout=timeout,
                            impersonate=alt,
                            allow_redirects=True,
                        )
                        if resp2.status_code == 200 and resp2.text and not is_waf_challenge(resp2.text):
                            return resp2.text
                    except Exception:
                        continue
            elif resp.status_code == 429:
                # Rate limited — back off and return None
                time.sleep(2.0)
                return None
        except Exception as e:
            print(f"[pipeline_utils] curl_cffi fetch failed for {url}: {e}")

    # --- Fallback: httpx ---
    try:
        resp = httpx.get(url, headers=merged_headers, timeout=timeout, follow_redirects=True)
        if resp.status_code == 200 and resp.text:
            if not is_waf_challenge(resp.text):
                return resp.text
    except Exception as e:
        print(f"[pipeline_utils] httpx fallback fetch failed for {url}: {e}")

    return None


def fetch_rss_feed(url: str, *, timeout: float = 10.0) -> Optional[str]:
    """
    Fetches an RSS feed URL.  RSS endpoints rarely deploy WAFs, so we use
    httpx directly to avoid unnecessary overhead.  Falls back to curl_cffi
    if the initial request fails.
    """
    try:
        resp = httpx.get(url, headers=RSS_HEADERS, timeout=timeout, follow_redirects=True)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        pass

    # Fallback: curl_cffi (some CDNs front RSS behind bot checks)
    if HAS_CURL_CFFI:
        try:
            resp = cffi_requests.get(
                url, headers=RSS_HEADERS, timeout=timeout,
                impersonate="chrome", allow_redirects=True,
            )
            if resp.status_code == 200 and resp.text:
                return resp.text
        except Exception:
            pass

    return None


# ---------------------------------------------------------------------------
# 3. CONTENT EXTRACTION (Trafilatura)
# ---------------------------------------------------------------------------
def extract_article_text(
    html: str,
    url: Optional[str] = None,
    *,
    include_metadata: bool = False,
) -> Optional[str]:
    """
    Extracts clean article body text from raw HTML using Trafilatura.
    Falls back to a basic BeautifulSoup heuristic if Trafilatura is unavailable.

    Returns None if the extracted text fails validation (too short, WAF page, etc.)
    """
    text = None

    if HAS_TRAFILATURA:
        try:
            text = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                favor_precision=True,
            )
        except Exception as e:
            print(f"[pipeline_utils] Trafilatura extraction failed: {e}")

    # Fallback: basic BS4 heuristic
    if not text:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["script", "style", "nav", "footer",
                                      "header", "noscript", "aside", "iframe"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
        except Exception:
            pass

    if text and is_valid_article(text):
        return text.strip()
    return None


def extract_article_metadata(html: str, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Extracts article metadata (title, author, date, description) via Trafilatura.
    """
    meta: Dict[str, Any] = {}
    if HAS_TRAFILATURA:
        try:
            result = trafilatura.bare_extraction(html, url=url, only_with_metadata=False)
            if result:
                meta["title"] = result.get("title", "")
                meta["author"] = result.get("author", "")
                meta["date"] = result.get("date", "")
                meta["description"] = result.get("description", "")
                meta["sitename"] = result.get("sitename", "")
        except Exception:
            pass
    return meta


def fetch_and_extract(url: str, *, timeout: float = 12.0) -> Optional[str]:
    """
    Convenience: fetch URL with TLS impersonation, then extract clean text.
    Returns None if fetch or extraction fails.
    """
    html = fetch_with_tls_impersonation(url, timeout=timeout)
    if not html:
        return None
    return extract_article_text(html, url=url)


# ---------------------------------------------------------------------------
# 4. GOOGLE NEWS URL RESOLUTION
# ---------------------------------------------------------------------------
def resolve_google_news_url(opaque_url: str) -> str:
    """
    Resolves an opaque Google News URL to the direct publisher URL using
    the batchexecute RPC handshake (via googlenewsdecoder).

    Falls back to naive redirect-following if the decoder is unavailable.
    Returns the original URL unchanged if resolution fails.
    """
    if not opaque_url or "news.google.com" not in opaque_url:
        return opaque_url

    # --- Primary: googlenewsdecoder batchexecute RPC ---
    if HAS_GNEWS_DECODER:
        try:
            result = decode_google_news_url(opaque_url, interval=1.0)
            if result and result.get("status"):
                decoded = result.get("decoded_url", "")
                if decoded and "news.google.com" not in decoded:
                    return decoded
        except Exception as e:
            print(f"[pipeline_utils] googlenewsdecoder failed: {e}")

    # --- Fallback: naive redirect following ---
    try:
        resp = httpx.head(opaque_url, headers=BROWSER_HEADERS, timeout=6.0, follow_redirects=True)
        final = str(resp.url)
        if final and "news.google.com" not in final and final != opaque_url:
            return final
    except Exception:
        pass
    try:
        resp = httpx.get(opaque_url, headers=BROWSER_HEADERS, timeout=6.0, follow_redirects=True)
        final = str(resp.url)
        if final and "news.google.com" not in final and final != opaque_url:
            return final
    except Exception:
        pass

    return opaque_url


# ---------------------------------------------------------------------------
# 5. MINHASH LSH NEAR-DUPLICATE DETECTION
# ---------------------------------------------------------------------------
# Default parameters for deduplication
MINHASH_NUM_PERM = 128
MINHASH_THRESHOLD = 0.85  # Jaccard similarity threshold

# In-memory LSH index (rebuilt per session / poll cycle)
_lsh_index: Optional[Any] = None
_lsh_store: Dict[str, str] = {}  # key -> representative text


def _tokenize(text: str, n: int = 3) -> List[str]:
    """Generates word n-grams from text for MinHash computation."""
    words = re.sub(r"[^\w\s]", "", text.lower()).split()
    if len(words) < n:
        return words
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def compute_minhash(text: str) -> Optional[Any]:
    """Computes a MinHash signature for the given text."""
    if not HAS_DATASKETCH:
        return None
    tokens = _tokenize(text)
    if not tokens:
        return None
    m = MinHash(num_perm=MINHASH_NUM_PERM)
    for token in tokens:
        m.update(token.encode("utf-8"))
    return m


def init_dedup_index():
    """Initializes (or resets) the in-memory MinHash LSH index."""
    global _lsh_index, _lsh_store
    if not HAS_DATASKETCH:
        return
    _lsh_index = MinHashLSH(threshold=MINHASH_THRESHOLD, num_perm=MINHASH_NUM_PERM)
    _lsh_store = {}


def is_near_duplicate(text: str, doc_id: str) -> bool:
    """
    Returns True if *text* is a near-duplicate of any document already
    indexed.  If it is not a duplicate, it is added to the index.

    Falls back to simple title-hash dedup if datasketch is unavailable.
    """
    global _lsh_index, _lsh_store

    if not HAS_DATASKETCH or _lsh_index is None:
        # Graceful degradation: exact-hash dedup
        h = hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()
        if h in _lsh_store:
            return True
        _lsh_store[h] = text
        return False

    mh = compute_minhash(text)
    if mh is None:
        return False

    # Query for near-duplicates
    try:
        candidates = _lsh_index.query(mh)
        if candidates:
            return True
    except Exception:
        return False

    # Not a duplicate — insert into the index
    try:
        _lsh_index.insert(doc_id, mh)
        _lsh_store[doc_id] = text
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# 6. SQLITE TTL CACHE-ASIDE
# ---------------------------------------------------------------------------
_CACHE_DB_PATH = os.path.join(os.path.dirname(__file__), "competitor_store.db")


def _get_cache_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_CACHE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_cache_tables():
    """Creates the TTL cache tables if they do not exist."""
    conn = _get_cache_conn()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS url_cache (
        cache_key   TEXT PRIMARY KEY,
        resolved_url TEXT NOT NULL,
        article_text TEXT,
        minhash_sig  TEXT,
        created_at   REAL NOT NULL,
        expires_at   REAL NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON url_cache (expires_at)")
    conn.commit()
    conn.close()


def _ttl_with_jitter(base_seconds: int = 86400, jitter_seconds: int = 3600) -> float:
    """Returns a TTL timestamp (epoch) with randomized jitter to prevent cache stampedes."""
    return time.time() + base_seconds + random.uniform(0, jitter_seconds)


def cache_lookup(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Cache-Aside READ: returns the cached entry if it exists and has not expired.
    Returns None on cache miss or expiry.
    """
    conn = _get_cache_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM url_cache WHERE cache_key = ? AND expires_at > ?",
        (cache_key, time.time()),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def cache_store(
    cache_key: str,
    resolved_url: str,
    article_text: Optional[str] = None,
    minhash_sig: Optional[str] = None,
    ttl_seconds: int = 86400,
    jitter_seconds: int = 3600,
):
    """
    Cache-Aside WRITE: stores a resolved URL and optionally the extracted
    article text and MinHash signature with a jittered TTL.
    """
    conn = _get_cache_conn()
    cursor = conn.cursor()
    now = time.time()
    expires = _ttl_with_jitter(ttl_seconds, jitter_seconds)
    cursor.execute("""
    INSERT INTO url_cache (cache_key, resolved_url, article_text, minhash_sig, created_at, expires_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(cache_key) DO UPDATE SET
        resolved_url = excluded.resolved_url,
        article_text = excluded.article_text,
        minhash_sig  = excluded.minhash_sig,
        created_at   = excluded.created_at,
        expires_at   = excluded.expires_at
    """, (cache_key, resolved_url, article_text, minhash_sig, now, expires))
    conn.commit()
    conn.close()


def cache_evict_expired():
    """Removes expired entries from the cache.  Call periodically."""
    conn = _get_cache_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM url_cache WHERE expires_at <= ?", (time.time(),))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted:
        print(f"[pipeline_utils] Evicted {deleted} expired cache entries.")


# ---------------------------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------------------------
# Create cache tables on import so they are always available.
try:
    init_cache_tables()
except Exception as e:
    print(f"[pipeline_utils] Warning: could not initialize cache tables: {e}")

# Initialize the dedup index
init_dedup_index()
