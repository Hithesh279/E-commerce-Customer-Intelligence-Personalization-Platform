"""
src/recommendation/content_based.py
Content-based recommendation engine utilizing TF-IDF product metadata representations and cosine similarity.
"""
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.utils.logging import get_logger

logger = get_logger("content_recommender")


class ContentBasedRecommender:
    """Content-based recommender engine using product catalog text representations."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.products_df: pd.DataFrame = pd.DataFrame()
        self.prod_to_idx: Dict[str, int] = {}
        self.idx_to_prod: Dict[int, str] = {}

    def fit(self, products_df: pd.DataFrame) -> "ContentBasedRecommender":
        """
        Fit TF-IDF matrix on product descriptions, categories, and brand tags.
        """
        self.products_df = products_df.copy().reset_index(drop=True)
        self.prod_to_idx = {pid: idx for idx, pid in enumerate(self.products_df["product_id"])}
        self.idx_to_prod = {idx: pid for idx, pid in enumerate(self.products_df["product_id"])}

        # Combined metadata corpus
        corpus = (
            self.products_df["category"] + " " +
            self.products_df["subcategory"] + " " +
            self.products_df["brand"] + " " +
            self.products_df["product_name"] + " " +
            self.products_df["product_description"]
        )

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=3500,
            stop_words="english",
            sublinear_tf=True,
        )
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        logger.info(f"Fitted content recommender similarity matrix shape: {self.similarity_matrix.shape}")
        return self

    def recommend_similar_products(
        self,
        product_id: str,
        top_k: int = 10,
        exclude_self: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return top-K most similar products to a given product."""
        if product_id not in self.prod_to_idx:
            logger.warning(f"Product {product_id} not found in content catalog.")
            return []

        idx = self.prod_to_idx[product_id]
        sim_scores = self.similarity_matrix[idx].copy()

        if exclude_self:
            sim_scores[idx] = -1.0

        top_indices = np.argsort(sim_scores)[::-1][:top_k]
        source_prod = self.products_df.iloc[idx]

        results = []
        for i in top_indices:
            row = self.products_df.iloc[i]
            results.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "price": row["price"],
                "score": round(float(sim_scores[i]), 4),
                "reason": f"Similar features to {source_prod['product_name']}",
            })
        return results

    def recommend_for_user(
        self,
        user_interacted_products: List[str],
        top_k: int = 10,
        exclude_seen: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Recommend items for a user by aggregating similarity vectors of products they interacted with.
        """
        if not user_interacted_products:
            return []

        valid_indices = [self.prod_to_idx[p] for p in user_interacted_products if p in self.prod_to_idx]
        if not valid_indices:
            return []

        # Average similarity vector across user's history
        user_profile_sim = self.similarity_matrix[valid_indices].mean(axis=0)

        if exclude_seen:
            for idx in valid_indices:
                user_profile_sim[idx] = -1.0

        top_indices = np.argsort(user_profile_sim)[::-1][:top_k]
        results = []
        for i in top_indices:
            row = self.products_df.iloc[i]
            results.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "price": row["price"],
                "score": round(float(user_profile_sim[i]), 4),
                "reason": f"Matches your interest in {row['category']} based on previous browsing",
            })
        return results
