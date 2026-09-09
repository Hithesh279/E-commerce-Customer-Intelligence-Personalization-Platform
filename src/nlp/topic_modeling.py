"""
src/nlp/topic_modeling.py
Discovers recurring customer complaints and praise themes using Non-Negative Matrix Factorization (NMF).
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from src.nlp.preprocessing import clean_text
from src.utils.config import MODELS_TOPIC_DIR, PROCESSED_DATA_DIR, RANDOM_SEED, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("topic_modeling")

TOPIC_DESCRIPTIVE_NAMES = {
    0: "Battery Life & Power Retention",
    1: "Camera Clarity & Optics",
    2: "Build Quality & Craftsmanship",
    3: "Pricing, Affordability & Value",
    4: "Shipping & Delivery Speed",
}


def train_topic_model(
    reviews_df: pd.DataFrame = None,
    num_topics: int = 5,
    num_top_words: int = 8,
) -> Tuple[NMF, TfidfVectorizer, List[Dict[str, Any]], pd.DataFrame]:
    """
    Train NMF topic model on reviews and extract key themes and complaint metrics.
    """
    ensure_directories()
    if reviews_df is None:
        from src.utils.config import RAW_DATA_DIR
        rw_path = RAW_DATA_DIR / "real_world_reviews.csv"
        if rw_path.exists():
            reviews_df = pd.read_csv(rw_path)
            if "product_id" not in reviews_df.columns:
                reviews_df["product_id"] = "PROD_0001"
            logger.info(f"Loaded {len(reviews_df)} authentic real-world reviews from internet dataset ({rw_path}) for topic modeling.")
        else:
            reviews_path = PROCESSED_DATA_DIR / "reviews.csv"
            reviews_df = pd.read_csv(reviews_path)
            logger.info(f"Loaded {len(reviews_df)} reviews from {reviews_path}.")

    # Text preprocessing with stopword removal
    cleaned_texts = reviews_df["review_text"].apply(lambda t: clean_text(t, remove_stopwords=True))

    tfidf_vec = TfidfVectorizer(
        max_df=0.85,
        min_df=3,
        max_features=2500,
        ngram_range=(1, 2),
    )
    tfidf_mat = tfidf_vec.fit_transform(cleaned_texts)

    nmf_model = NMF(
        n_components=num_topics,
        random_state=RANDOM_SEED,
        max_iter=400,
        init="nndsvda",
    )
    W = nmf_model.fit_transform(tfidf_mat)
    H = nmf_model.components_

    feature_names = tfidf_vec.get_feature_names_out()

    # Assign dominant topic to each review
    dominant_topics = np.argmax(W, axis=1)
    reviews_with_topics = reviews_df.copy()
    reviews_with_topics["topic_id"] = dominant_topics
    reviews_with_topics["topic_name"] = reviews_with_topics["topic_id"].map(
        lambda tid: TOPIC_DESCRIPTIVE_NAMES.get(tid, f"Topic {tid}")
    )

    # Derive topic summaries
    topic_summaries = []
    total_reviews = len(reviews_with_topics)

    for topic_idx in range(num_topics):
        top_word_indices = H[topic_idx].argsort()[:-num_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_word_indices]

        topic_subset = reviews_with_topics[reviews_with_topics["topic_id"] == topic_idx]
        count = len(topic_subset)
        pct = round((count / total_reviews) * 100, 2)
        avg_rating = round(float(topic_subset["rating"].mean()), 2)

        # Top affected products
        top_products = topic_subset["product_id"].value_counts().head(5).to_dict()

        summary_entry = {
            "topic_id": topic_idx,
            "topic_name": TOPIC_DESCRIPTIVE_NAMES.get(topic_idx, f"Topic {topic_idx}"),
            "top_words": top_words,
            "review_count": count,
            "percentage_of_reviews": pct,
            "avg_rating": avg_rating,
            "top_affected_products": top_products,
        }
        topic_summaries.append(summary_entry)
        logger.info(f"Topic {topic_idx} ({summary_entry['topic_name']}): {top_words[:4]} | {count} reviews ({pct}%) | Avg Rating: {avg_rating}")

    # Save artifacts
    model_path = MODELS_TOPIC_DIR / "topic_model.joblib"
    vec_path = MODELS_TOPIC_DIR / "topic_vectorizer.joblib"
    summary_path = MODELS_TOPIC_DIR / "topic_summaries.json"

    joblib.dump(nmf_model, model_path)
    joblib.dump(tfidf_vec, vec_path)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(topic_summaries, f, indent=2)

    logger.info(f"Saved topic model artifacts to: {MODELS_TOPIC_DIR}")
    return nmf_model, tfidf_vec, topic_summaries, reviews_with_topics


if __name__ == "__main__":
    train_topic_model()
