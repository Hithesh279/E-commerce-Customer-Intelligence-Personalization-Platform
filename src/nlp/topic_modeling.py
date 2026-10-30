"""
src/nlp/topic_modeling.py
Discovers recurring themes in review text with Non-Negative Matrix Factorization (NMF).

Topics are labelled by their most characteristic words, derived from the fitted model; nothing is
hand-assigned to a topic index. Product attribution is reported only when the input has a
product_id column. Otherwise no product is attributed to any topic.
"""
import json
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from src.nlp.preprocessing import clean_text
from src.utils.config import MODELS_TOPIC_DIR, PROCESSED_DATA_DIR, RANDOM_SEED, RAW_DATA_DIR, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("topic_modeling")


def topic_label(top_words: List[str], max_words: int = 3) -> str:
    """Human-readable label built from a topic's strongest words."""
    if not top_words:
        return "Unlabelled topic"
    return ", ".join(top_words[:max_words])


def _load_default_reviews() -> Tuple[pd.DataFrame, str]:
    rw_path = RAW_DATA_DIR / "real_world_reviews.csv"
    if rw_path.exists():
        return pd.read_csv(rw_path), rw_path.name
    path = PROCESSED_DATA_DIR / "reviews.csv"
    return pd.read_csv(path), path.name


def train_topic_model(
    reviews_df: pd.DataFrame = None,
    num_topics: int = 5,
    num_top_words: int = 8,
) -> Tuple[NMF, TfidfVectorizer, List[Dict[str, Any]], pd.DataFrame]:
    """Train an NMF topic model on review text and summarize each topic."""
    ensure_directories()
    if reviews_df is None:
        reviews_df, source_name = _load_default_reviews()
    else:
        source_name = "caller-provided DataFrame"

    reviews_df = reviews_df.dropna(subset=["review_text"]).reset_index(drop=True)
    has_products = "product_id" in reviews_df.columns

    cleaned_texts = reviews_df["review_text"].astype(str).apply(lambda t: clean_text(t, remove_stopwords=True))
    tfidf_vec = TfidfVectorizer(max_df=0.85, min_df=3, max_features=2500, ngram_range=(1, 2))
    tfidf_mat = tfidf_vec.fit_transform(cleaned_texts)

    nmf_model = NMF(n_components=num_topics, random_state=RANDOM_SEED, max_iter=400, init="nndsvda")
    W = nmf_model.fit_transform(tfidf_mat)
    H = nmf_model.components_
    feature_names = tfidf_vec.get_feature_names_out()

    reviews_with_topics = reviews_df.copy()
    reviews_with_topics["topic_id"] = np.argmax(W, axis=1)
    total_reviews = len(reviews_with_topics)

    topic_summaries: List[Dict[str, Any]] = []
    for topic_idx in range(num_topics):
        top_word_indices = H[topic_idx].argsort()[::-1][:num_top_words]
        top_words = [str(feature_names[i]) for i in top_word_indices]

        subset = reviews_with_topics[reviews_with_topics["topic_id"] == topic_idx]
        count = int(len(subset))
        avg_rating = round(float(subset["rating"].mean()), 2) if ("rating" in subset.columns and count) else None

        top_products = {}
        if has_products:
            known = subset["product_id"].dropna().astype(str)
            top_products = {str(k): int(v) for k, v in known.value_counts().head(5).items()}

        summary = {
            "topic_id": topic_idx,
            "topic_name": topic_label(top_words),
            "top_words": top_words,
            "review_count": count,
            "percentage_of_reviews": round(count / total_reviews * 100, 2) if total_reviews else 0.0,
            "avg_rating": avg_rating,
            "top_affected_products": top_products,
            "product_attribution": "available" if has_products else "unavailable: no product_id column",
            "data_source": source_name,
            "documents_trained": total_reviews,
        }
        topic_summaries.append(summary)
        logger.info(f"Topic {topic_idx} ({summary['topic_name']}): {count} reviews ({summary['percentage_of_reviews']}%)")

    ensure_directories()
    joblib.dump(nmf_model, MODELS_TOPIC_DIR / "topic_model.joblib")
    joblib.dump(tfidf_vec, MODELS_TOPIC_DIR / "topic_vectorizer.joblib")
    with open(MODELS_TOPIC_DIR / "topic_summaries.json", "w", encoding="utf-8") as f:
        json.dump(topic_summaries, f, indent=2)

    logger.info(f"Saved topic model artifacts to: {MODELS_TOPIC_DIR}")
    return nmf_model, tfidf_vec, topic_summaries, reviews_with_topics


if __name__ == "__main__":
    train_topic_model()
