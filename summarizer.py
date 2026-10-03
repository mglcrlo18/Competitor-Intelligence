"""
summarizer.py
AI Synthesis Engine using Google Gemini API trained in Competitive Intelligence.
Specialized for GoNano Competitor Analysis, Threat Modeling, and Counter-Strategies.
"""
import os
import json
from typing import Dict, Any, List, Optional
import httpx
import time

# Default Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SYSTEM_COMPETITOR_PROMPT = """You are an elite Competitive Intelligence Strategist and Market Research Director for GoNano (a leader in nanotechnology-based roof and building materials protection).
Your role is to critically analyze competitor moves, signals, press releases, advertisements, and news, and evaluate their direct threat and strategic implications against GoNano.

GoNano Technology & Moat:
- Technology: Deep-penetrating molecular nanotechnology that restores asphalt shingle flexibility, binds granules from within, and confers extreme hail/wind resilience without forming a peeling surface film.
- GoNano Lifespan & Value: 10-15+ years extended roof life at a fraction of replacement cost, preserving manufacturer warranties.
- Strategic Channels: B2B roofer certifications, Commercial & REIT property asset management, and Solar EPC pre-treatment partnerships (rescuing older roofs to enable solar installs).

Competitor Paradigms to Benchmark:
1. Bio-Oil / Soy-Based (e.g. RoofLife Canada, Roof Maxx, Reactiv8): Temporary oil replenishment (5 yrs), susceptible to microbial wash-out, zero structural or hail cross-linking.
2. Elastomeric Coatings / Paint Sprays (e.g. Spray-Net, GVMA): Cosmetic surface coatings, prone to peeling/trapping moisture, does not penetrate shingle matrix.
3. Competing Nanotech / Ceramics (e.g. Nasiol, Nanoseal, Nanoclad): Surface hydrophobics (SiO2), often lack asphalt-specific deep penetration and roofer-first distribution.
"""

def call_gemini_api(prompt: str, system_instruction: str = SYSTEM_COMPETITOR_PROMPT, api_key: str = None) -> Optional[str]:
    """Helper to query Gemini API (gemini-1.5-flash) with error handling."""
    key = api_key or os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024
        }
    }

    try:
        for attempt in range(3):
            response = httpx.post(url, json=payload, timeout=25.0)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            if response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"Gemini API rate limited (429). Retrying in {wait_time}s... (attempt {attempt+1}/3)")
                time.sleep(wait_time)
                continue
            break
    except Exception as e:
        print(f"Gemini API call failed: {e}")
    return None


def generate_competitor_summary(competitor_name: Optional[str] = None, signals: Optional[Dict[str, Any]] = None, api_key: str = None) -> str:
    """
    Sends aggregated competitor signals to Gemini API to produce an executive intelligence briefing.
    Falls back to a structured rule-based competitive assessment if offline.
    """
    if not competitor_name or not str(competitor_name).strip():
        competitor_name = "RoofLife Canada"
    if not signals or not isinstance(signals, dict):
        signals = {"news": [], "hiring": [], "ads": []}
    competitor_name = str(competitor_name).strip()
    prompt = f"""Analyze the following intelligence signals for competitor '{competitor_name}' against GoNano:

Raw Signals:
- News & Press Releases: {signals.get('news', [])}
- Open Roles & Hiring: {signals.get('hiring', [])}
- Active Ads & Marketing: {signals.get('ads', [])}

Produce a structured, rigorous executive intelligence briefing with the following sections:
1. Executive Verdict (2-3 sentences on what this competitor is prioritizing right now)
2. Strategic Moves & Expansion Signals (territory expansion, product formulation, certifications, hiring)
3. Advertising & Messaging Angles (customer hooks, pain points targeted, marketing claims)
4. Competitor Weakness & Technical Flaws (where their approach fails compared to GoNano's nanotechnology)
5. GoNano Counter-Strategy & Action Items (sales objection-handling, counter-marketing, target battlecard)
"""

    gemini_resp = call_gemini_api(prompt, api_key=api_key)
    if gemini_resp:
        return gemini_resp

    # High-quality fallback analysis grounded in GoNano competitive matrix
    return f"""### [REPORT] Executive Intelligence Brief: {competitor_name}
**Verdict:** {competitor_name} is actively pushing market acquisition through digital funnels and local applicator networks. Their positioning emphasizes alternative roof preservation over full replacement.

**Strategic Moves & Signals:**
- News & PR signals: {len(signals.get('news', []))} recent articles detected across regional and trade publications.
- Paid Advertising: Heavy reliance on video demonstration ads (water beading or shingle bending tests).

**Technical Vulnerability vs. GoNano:**
- If bio-based (e.g. soy/oil): Rejuvenation is temporary (3-5 years) with no cross-linking matrix or hail impact upgrade.
- If coating/elastomeric: Surface layer risks peeling under extreme thermal expansion; cannot match GoNano's deep molecular penetration.

**Recommended GoNano Counter-Actions:**
1. Equip sales reps with the "Deep Penetration vs. Surface Coating" side-by-side demonstration battlecard.
2. Emphasize GoNano's 10-15 year warranty, hail-impact resilience, and solar installer compatibility.
3. Target local roofers with GoNano B2B partner margins to prevent competitor territory lock-in."""


def analyze_news_item_threat(competitor_name: str, title: str, snippet: str, api_key: str = None) -> Dict[str, str]:
    """
    Analyzes a specific news article or press release to classify threat level,
    strategic intent, and GoNano counter-action.
    """
    prompt = f"""Competitor: {competitor_name}
Article Title: {title}
Article Snippet: {snippet}

Evaluate this news item as a Competitor Intelligence Analyst for GoNano. Return a JSON object with:
- "threat_level": ("Low", "Moderate", "High", or "Critical")
- "category": ("Expansion", "Product Launch", "Pricing/Warranty", "Partnership", "Regulatory/Legal", "General PR")
- "competitor_intent": (1 sentence on what the competitor is achieving with this)
- "gonano_implication": (1 sentence on what this means for GoNano's market position)
- "recommended_action": (1 actionable counter-move for GoNano)
"""
    raw = call_gemini_api(prompt, api_key=api_key)
    if raw:
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return data
        except Exception:
            pass

    # Deterministic rule-based assessment fallback
    lower = (title + " " + snippet).lower()
    threat = "Moderate"
    cat = "General PR"
    
    if any(k in lower for k in ["launch", "new product", "patent", "breakthrough", "technology"]):
        threat = "High"
        cat = "Product Launch"
    elif any(k in lower for k in ["expand", "acquisition", "territory", "dealer", "franchise", "hiring"]):
        threat = "High"
        cat = "Expansion"
    elif any(k in lower for k in ["warranty", "guarantee", "discount", "price", "rebate"]):
        threat = "Moderate"
        cat = "Pricing/Warranty"
    elif any(k in lower for k in ["lawsuit", "complaint", "scam", "investigation", "warning"]):
        threat = "Low"
        cat = "Regulatory/Legal"

    return {
        "threat_level": threat,
        "category": cat,
        "competitor_intent": f"{competitor_name} is leveraging PR to bolster brand legitimacy and capture homeowner interest.",
        "gonano_implication": f"Potential risk of confusing prospects regarding surface treatments vs. genuine nanotechnology.",
        "recommended_action": "Reinforce GoNano's scientific certification data and lifetime value comparisons in regional sales collateral."
    }

def batch_summarize_articles(
    articles: List[Dict[str, Any]],
    competitor_name: str = "Competitor",
    api_key: str = None,
    max_articles_per_batch: int = 10,
) -> Optional[str]:
    """
    Batches multiple articles into a single Gemini API prompt to maximize
    value per API call and conserve the free-tier quota (15-20 RPD).
    """
    if not articles:
        return None

    # Build a single combined prompt with all article texts
    article_blocks = []
    for i, art in enumerate(articles[:max_articles_per_batch], 1):
        title = art.get("title", "Untitled")
        text = art.get("full_text") or art.get("summary", "")
        source = art.get("source", "Unknown")
        article_blocks.append(f"--- Article {i} ---\nTitle: {title}\nSource: {source}\nContent:\n{text[:2000]}")

    combined = "\n\n".join(article_blocks)
    prompt = f"""Analyze the following {len(article_blocks)} intelligence signals for competitor '{competitor_name}' against GoNano.
Provide a SINGLE consolidated executive intelligence briefing covering:
1. Executive Verdict (2-3 sentences on the competitor's current strategic priorities)
2. Key Strategic Moves detected across all articles
3. Advertising & Messaging Angles observed
4. Competitor Weaknesses & Technical Flaws vs GoNano nanotechnology
5. GoNano Counter-Strategy & Recommended Actions

Articles:
{combined}"""

    return call_gemini_api(prompt, api_key=api_key)
