"""
src/nlp/aspect_extraction.py
Aspect-Based Sentiment Analysis (ABSA).
Extracts fine-grained sentiment across 11 key product aspects:
(battery, camera, display, performance, quality, price, comfort, durability, delivery, packaging, design).
"""
import re
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config import ASPECT_LIST, PROCESSED_DATA_DIR, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("aspect_extraction")

# Lexicon keywords and synonyms for the 11 aspects
ASPECT_LEXICON: Dict[str, List[str]] = {
    "battery": ["battery", "charge", "charging", "battery life", "charger", "power"],
    "camera": ["camera", "photo", "picture", "lens", "sensor", "resolution", "video", "zoom"],
    "display": ["display", "screen", "panel", "oled", "brightness", "refresh rate", "pixels"],
    "performance": ["performance", "speed", "fast", "responsive", "multitasking", "lag", "latency", "stutter", "slow"],
    "quality": ["quality", "material", "craftsmanship", "sturdy", "premium", "build", "construction", "flimsy"],
    "price": ["price", "cost", "value", "money", "expensive", "affordable", "cheap", "worth", "markup"],
    "comfort": ["comfort", "comfortable", "fit", "ergonomic", "lightweight", "soreness", "cushioning", "wear"],
    "durability": ["durability", "durable", "rugged", "longevity", "last", "broke", "fragile", "fractured"],
    "delivery": ["delivery", "shipping", "courier", "arrival", "delivered", "transit", "delayed", "late"],
    "packaging": ["packaging", "box", "package", "wrapped", "unboxing", "sealed", "pack", "bubble wrap"],
    "design": ["design", "aesthetic", "look", "appearance", "stylish", "sleek", "clunky", "finish"],
}

# Positive and negative sentiment indicators within aspect context
POSITIVE_CLUES = {
    "exceptional", "outstanding", "great", "excellent", "superb", "crystal", "clear",
    "vibrant", "blazing", "fast", "responsive", "premium", "sturdy", "solid", "remarkable",
    "value", "affordable", "worth", "comfortable", "soothing", "durable", "rugged", "prompt",
    "transparent", "secure", "eco-friendly", "elegant", "sleek", "modern", "appealing", "good",
    "love", "best", "perfect", "fantastic", "smooth", "high", "lasts", "lasting", "reliable",
    "impressive", "easy", "pleased", "delighted", "recommend", "bright", "sharp"
}

NEGATIVE_CLUES = {
    "terrible", "draining", "dies", "sluggishly", "blurry", "disappointing", "noisy", "subpar",
    "dim", "glare", "washed", "dull", "sluggish", "stutter", "lag", "slow", "cheap", "flimsy",
    "poor", "fragile", "overpriced", "expensive", "awkward", "soreness", "discomfort", "uncomfortable",
    "lacks", "fractured", "broke", "delays", "late", "damaged", "dented", "clunky", "outdated",
    "bad", "worst", "hate", "awful", "horrible", "defect", "useless"
}


def extract_aspect_sentiment_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extract all mentioned aspects and compute localized sentiment score and label.

    Parameters
    ----------
    text : str
        Review text.

    Returns
    -------
    List[Dict[str, Any]]
        List of dicts with keys: aspect, sentiment, sentiment_score, snippet.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Split text into clauses/sentences
    clauses = re.split(r"[.!?,;]+|\bbut\b|\bhowever\b|\balso\b|\band\b", text, flags=re.IGNORECASE)
    results = []
    found_aspects = set()

    for clause in clauses:
        clause_clean = clause.strip().lower()
        if not clause_clean:
            continue

        clause_words = set(re.findall(r"\b\w+\b", clause_clean))

        for aspect, keywords in ASPECT_LEXICON.items():
            if aspect in found_aspects:
                continue

            # Check if any keyword matches
            matches = any(re.search(r"\b" + re.escape(kw) + r"\b", clause_clean) for kw in keywords)
            if matches:
                # Score local clause
                pos_hits = len(clause_words.intersection(POSITIVE_CLUES))
                neg_hits = len(clause_words.intersection(NEGATIVE_CLUES))

                if pos_hits > neg_hits:
                    sentiment = "Positive"
                    score = min(1.0, 0.4 + 0.25 * (pos_hits - neg_hits))
                elif neg_hits > pos_hits:
                    sentiment = "Negative"
                    score = max(-1.0, -0.4 - 0.25 * (neg_hits - pos_hits))
                else:
                    sentiment = "Neutral"
                    score = 0.0

                results.append({
                    "aspect": aspect,
                    "sentiment": sentiment,
                    "sentiment_score": round(score, 2),
                    "snippet": clause.strip(),
                })
                found_aspects.add(aspect)

    return results


def process_reviews_absa(reviews_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Run ABSA extraction over entire reviews dataset.
    Generates structured review_aspects table and persists to data/processed/.
    """
    ensure_directories()
    if reviews_df is None:
        reviews_path = PROCESSED_DATA_DIR / "reviews.csv"
        reviews_df = pd.read_csv(reviews_path)

    logger.info(f"Extracting aspect sentiments across {len(reviews_df)} reviews...")

    aspect_records = []
    for _, row in reviews_df.iterrows():
        rid = row["review_id"]
        pid = row["product_id"]
        extracted = extract_aspect_sentiment_from_text(row["review_text"])

        for item in extracted:
            aspect_records.append({
                "review_id": rid,
                "product_id": pid,
                "aspect": item["aspect"],
                "sentiment": item["sentiment"],
                "sentiment_score": item["sentiment_score"],
            })

    aspects_df = pd.DataFrame(aspect_records)
    out_path = PROCESSED_DATA_DIR / "review_aspects.csv"
    aspects_df.to_csv(out_path, index=False)

    logger.info(f"Generated {len(aspects_df)} aspect-sentiment observations. Saved to: {out_path}")
    return aspects_df


def aggregate_aspect_metrics(
    aspects_df: pd.DataFrame,
    products_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compute aspect-level satisfaction score and volume aggregated by product and category."""
    merged = aspects_df.merge(products_df[["product_id", "product_name", "category"]], on="product_id", how="left")

    summary = merged.groupby(["category", "aspect"]).agg(
        total_mentions=("review_id", "count"),
        avg_sentiment_score=("sentiment_score", "mean"),
        positive_pct=("sentiment", lambda s: round((s == "Positive").mean() * 100, 1)),
        negative_pct=("sentiment", lambda s: round((s == "Negative").mean() * 100, 1)),
    ).reset_index()

    summary["avg_sentiment_score"] = summary["avg_sentiment_score"].round(3)
    return summary


if __name__ == "__main__":
    process_reviews_absa()
