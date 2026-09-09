"""
src/recommendation/train.py
Fits and serializes recommendation models to models/recommendation/ for rapid inference.
"""
import json
from pathlib import Path
import joblib
import pandas as pd

from src.recommendation.collaborative import CollaborativeRecommender
from src.recommendation.content_based import ContentBasedRecommender
from src.recommendation.popularity import PopularityRecommender
from src.utils.config import (
    HYBRID_WEIGHTS,
    MODELS_RECOMMENDATION_DIR,
    PROCESSED_DATA_DIR,
    ensure_directories,
)
from src.utils.logging import get_logger

logger = get_logger("recommendation_train")


def train_and_save_recommenders():
    """Fit all recommendation engines on processed data and serialize artifacts."""
    ensure_directories()
    products_df = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")
    transactions_df = pd.read_csv(PROCESSED_DATA_DIR / "transactions.csv")
    reviews_df = pd.read_csv(PROCESSED_DATA_DIR / "reviews.csv")
    interactions_df = pd.read_csv(PROCESSED_DATA_DIR / "interactions.csv")

    logger.info("Training and serializing recommendation models...")

    # 1. Popularity Engine
    pop_engine = PopularityRecommender().fit(transactions_df, products_df, reviews_df)
    joblib.dump(pop_engine, MODELS_RECOMMENDATION_DIR / "popularity_model.joblib")

    # 2. Content Engine
    content_engine = ContentBasedRecommender().fit(products_df)
    joblib.dump(content_engine, MODELS_RECOMMENDATION_DIR / "content_model.joblib")

    # 3. Collaborative Engine
    collab_engine = CollaborativeRecommender(n_factors=25).fit(interactions_df, products_df)
    joblib.dump(collab_engine, MODELS_RECOMMENDATION_DIR / "collaborative_model.joblib")

    # 4. Save metadata and weights
    meta = {
        "num_products": len(products_df),
        "num_interactions": len(interactions_df),
        "hybrid_weights": HYBRID_WEIGHTS,
    }
    with open(MODELS_RECOMMENDATION_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Saved all recommendation models to {MODELS_RECOMMENDATION_DIR}")


if __name__ == "__main__":
    train_and_save_recommenders()
