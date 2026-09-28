"""
analytics_engine.py
Analytics, Sentiment, Share of Voice (SOV), and Topic Cloud Engine
designed to replicate Awario and Sprout Social competitive listening dashboards.
"""
import re
from collections import Counter
from typing import Dict, List, Any
import pandas as pd

# Core domain sentiment lexicons (Roofing, Coatings, Service, Customer Reviews)
POSITIVE_WORDS = {
    "great", "excellent", "saved", "durable", "best", "good", "protect", "warranty",
    "recommend", "clean", "effective", "waterproof", "restoration", "flexible",
    "certified", "quality", "proven", "eco", "growth", "approved", "strong", "satisfied"
}

NEGATIVE_WORDS = {
    "scam", "waste", "expensive", "peeling", "cracking", "complaint", "fail", "lawsuit",
    "disaster", "cancelled", "broken", "leak", "damage", "strike", "bad", "terrible",
    "delay", "warning", "fake", "overpriced", "dispute", "loss"
}

STOP_WORDS = {
    "the", "and", "a", "to", "of", "in", "is", "for", "that", "this", "it", "on",
    "with", "as", "at", "by", "from", "an", "be", "are", "was", "will", "have",
    "or", "your", "you", "we", "our", "all", "so", "if", "not", "new", "about",
    "out", "up", "one", "more", "can", "into", "their", "what", "how", "has"
}

def analyze_sentiment(texts: List[str]) -> Dict[str, Any]:
    """
    Computes sentiment proportions (Positive, Neutral, Negative) across a text corpus.
    """
    pos_count = 0
    neg_count = 0
    neu_count = 0
    
    for text in texts:
        clean = text.lower()
        words = set(re.findall(r"\b[a-z]{3,}\b", clean))
        pos_hits = len(words.intersection(POSITIVE_WORDS))
        neg_hits = len(words.intersection(NEGATIVE_WORDS))
        
        if pos_hits > neg_hits:
            pos_count += 1
        elif neg_hits > pos_hits:
            neg_count += 1
        else:
            neu_count += 1
            
    total = max(pos_count + neg_count + neu_count, 1)
    return {
        "positive": round((pos_count / total) * 100, 1),
        "negative": round((neg_count / total) * 100, 1),
        "neutral": round((neu_count / total) * 100, 1),
        "counts": {
            "positive": pos_count,
            "negative": neg_count,
            "neutral": neu_count,
            "total": total
        }
    }


def compute_share_of_voice(competitor_counts: Dict[str, int]) -> pd.DataFrame:
    """
    Builds Share of Voice (SOV) data comparing competitor presence.
    """
    total = sum(competitor_counts.values()) or 1
    rows = []
    for comp, count in competitor_counts.items():
        pct = round((count / total) * 100, 1)
        rows.append({"Competitor": comp, "Mentions": count, "Share of Voice (%)": pct})
    return pd.DataFrame(rows)


def extract_topic_cloud(texts: List[str], top_n: int = 25) -> List[Dict[str, Any]]:
    """
    Extracts recurring keywords and topics to populate the Topic Cloud widget.
    """
    counter = Counter()
    for text in texts:
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        for w in words:
            if w not in STOP_WORDS and not w.isdigit():
                counter[w] += 1
                
    topics = []
    for word, freq in counter.most_common(top_n):
        topics.append({"topic": word, "frequency": freq})
    return topics
