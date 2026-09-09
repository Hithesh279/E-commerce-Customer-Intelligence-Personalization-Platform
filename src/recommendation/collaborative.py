"""
src/recommendation/collaborative.py
Collaborative filtering recommendation engine based on implicit interaction matrix factorization (TruncatedSVD).
"""
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfTransformer

from src.features.interaction_matrix import build_interaction_matrix
from src.utils.config import RANDOM_SEED
from src.utils.logging import get_logger

logger = get_logger("collaborative_recommender")


class CollaborativeRecommender:
    """Collaborative filtering recommender using Matrix Factorization."""

    def __init__(self, n_factors: int = 25):
        self.n_factors = n_factors
        self.svd_model: Optional[TruncatedSVD] = None
        self.scaler: Optional[TfidfTransformer] = None
        self.user_factors: Optional[np.ndarray] = None
        self.item_factors: Optional[np.ndarray] = None
        self.user_to_idx: Dict[str, int] = {}
        self.idx_to_user: Dict[int, str] = {}
        self.item_to_idx: Dict[str, int] = {}
        self.idx_to_item: Dict[int, str] = {}
        self.products_df: pd.DataFrame = pd.DataFrame()
        self.seen_interactions: Dict[str, set] = {}

    def fit(
        self,
        interactions_df: pd.DataFrame,
        products_df: pd.DataFrame,
    ) -> "CollaborativeRecommender":
        """
        Build interaction matrix and compute SVD latent factors.
        """
        self.products_df = products_df.copy()
        mat, u2i, i2u, it2i, i2it = build_interaction_matrix(interactions_df)
        self.user_to_idx = u2i
        self.idx_to_user = i2u
        self.item_to_idx = it2i
        self.idx_to_item = i2it

        # Track seen products per customer
        self.seen_interactions = interactions_df.groupby("customer_id")["product_id"].apply(set).to_dict()

        # Apply TF-IDF scaling on interaction matrix to temper high-frequency item biases
        self.scaler = TfidfTransformer(sublinear_tf=True)
        scaled_mat = self.scaler.fit_transform(mat)

        # Fit TruncatedSVD on scaled matrix
        effective_factors = min(self.n_factors, mat.shape[1] - 1, mat.shape[0] - 1)
        self.svd_model = TruncatedSVD(n_components=effective_factors, random_state=RANDOM_SEED)
        self.user_factors = self.svd_model.fit_transform(scaled_mat)  # (n_users, k)
        self.item_factors = self.svd_model.components_.T              # (n_items, k)

        var_explained = self.svd_model.explained_variance_ratio_.sum()
        logger.info(f"Fitted SVD Collaborative Filter ({effective_factors} factors). Variance explained: {var_explained:.2%}")
        return self

    def recommend(
        self,
        customer_id: str,
        top_k: int = 10,
        exclude_seen: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate top-K collaborative filtering recommendations for a customer.
        Returns empty list for cold-start users (handled by hybrid/fallback).
        """
        if customer_id not in self.user_to_idx:
            logger.info(f"Customer {customer_id} is cold-start for collaborative filtering.")
            return []

        u_idx = self.user_to_idx[customer_id]
        u_vec = self.user_factors[u_idx]  # (k,)
        # Predicted affinity scores across all items
        scores = np.dot(self.item_factors, u_vec)

        if exclude_seen and customer_id in self.seen_interactions:
            seen_items = self.seen_interactions[customer_id]
            for itm in seen_items:
                if itm in self.item_to_idx:
                    scores[self.item_to_idx[itm]] = -np.inf

        top_item_indices = np.argsort(scores)[::-1][:top_k]

        prod_lookup = dict(zip(self.products_df["product_id"], self.products_df["product_name"]))
        cat_lookup = dict(zip(self.products_df["product_id"], self.products_df["category"]))
        price_lookup = dict(zip(self.products_df["product_id"], self.products_df["price"]))

        results = []
        for idx in top_item_indices:
            pid = self.idx_to_item[idx]
            score_val = float(scores[idx])
            if np.isneginf(score_val):
                continue
            results.append({
                "product_id": pid,
                "product_name": prod_lookup.get(pid, "Unknown"),
                "category": cat_lookup.get(pid, "General"),
                "price": price_lookup.get(pid, 0.0),
                "score": round(score_val, 4),
                "reason": "Customers with similar browsing and purchase patterns also favored this",
            })
        return results

    def get_user_item_score_dict(self, customer_id: str) -> Dict[str, float]:
        """Return dict of product_id -> collaborative score for user."""
        if customer_id not in self.user_to_idx:
            return {}
        u_idx = self.user_to_idx[customer_id]
        u_vec = self.user_factors[u_idx]
        scores = np.dot(self.item_factors, u_vec)
        return {self.idx_to_item[i]: float(scores[i]) for i in range(len(scores))}
