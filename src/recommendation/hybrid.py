"""
src/recommendation/hybrid.py
Hybrid recommendation engine blending Collaborative Filtering, Content-Based Similarity,
and Popularity with score normalization and graceful cold-start fallback.
"""
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.recommendation.collaborative import CollaborativeRecommender
from src.recommendation.content_based import ContentBasedRecommender
from src.recommendation.explainability import generate_recommendation_reason
from src.recommendation.popularity import PopularityRecommender
from src.utils.config import HYBRID_WEIGHTS
from src.utils.logging import get_logger

logger = get_logger("hybrid_recommender")


def min_max_normalize(scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize score values in dict to [0.0, 1.0] range."""
    if not scores:
        return {}
    vals = list(scores.values())
    min_v, max_v = min(vals), max(vals)
    if max_v == min_v:
        return {k: 0.5 for k in scores}
    return {k: (v - min_v) / (max_v - min_v) for k, v in scores.items()}


class HybridRecommender:
    """Configurable ensemble hybrid recommender engine."""

    def __init__(
        self,
        popularity_engine: PopularityRecommender,
        content_engine: ContentBasedRecommender,
        collaborative_engine: CollaborativeRecommender,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.pop_engine = popularity_engine
        self.content_engine = content_engine
        self.collab_engine = collaborative_engine
        self.weights = weights or HYBRID_WEIGHTS.copy()
        self.products_df = self.content_engine.products_df
        self.user_history: Dict[str, List[str]] = {}

    def set_user_history(self, interactions_df: pd.DataFrame) -> None:
        """Cache user interaction history for content and cold-start detection."""
        self.user_history = (
            interactions_df.groupby("customer_id")["product_id"].apply(list).to_dict()
        )

    def recommend(
        self,
        customer_id: str,
        top_k: int = 10,
        exclude_seen: bool = True,
        preferred_category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate top-K hybrid recommendations for a given customer.
        Dynamically handles cold-start users.
        """
        history = self.user_history.get(customer_id, [])
        is_cold_start = len(history) == 0

        # Cold-start fallback directly to popularity (optionally category-filtered)
        if is_cold_start:
            pop_recs = self.pop_engine.recommend(
                customer_id=customer_id,
                category=preferred_category,
                top_k=top_k,
            )
            for r in pop_recs:
                r["reason"] = generate_recommendation_reason(
                    r["product_name"], r["category"], 0.0, 0.0, r["score"], is_cold_start=True
                )
            return pop_recs

        # 1. Collaborative scores
        raw_collab_scores = self.collab_engine.get_user_item_score_dict(customer_id)
        norm_collab = min_max_normalize(raw_collab_scores)

        # 2. Content scores based on user history
        norm_content = {}
        if history:
            content_recs = self.content_engine.recommend_for_user(history, top_k=len(self.products_df), exclude_seen=False)
            raw_content = {r["product_id"]: r["score"] for r in content_recs}
            norm_content = min_max_normalize(raw_content)

        # 3. Popularity scores
        raw_pop = dict(zip(self.pop_engine.popular_products["product_id"], self.pop_engine.popular_products["popularity_score"]))
        norm_pop = min_max_normalize(raw_pop)

        # Candidate products
        seen_set = set(history) if exclude_seen else set()
        all_pids = [p for p in self.products_df["product_id"] if p not in seen_set]

        w_pop = self.weights.get("popularity", 0.45)
        w_collab = self.weights.get("collaborative", 0.35)
        w_content = self.weights.get("content", 0.20)

        # Rebalance weights if user has sparse collaborative signal
        if not norm_collab:
            w_collab = 0.0
            w_content = 0.35
            w_pop = 0.65

        prod_lookup = dict(zip(self.products_df["product_id"], self.products_df["product_name"]))
        cat_lookup = dict(zip(self.products_df["product_id"], self.products_df["category"]))
        price_lookup = dict(zip(self.products_df["product_id"], self.products_df["price"]))

        scored_items = []
        for pid in all_pids:
            c_score = norm_collab.get(pid, 0.0)
            cnt_score = norm_content.get(pid, 0.0)
            p_score = norm_pop.get(pid, 0.0)

            final_score = (w_collab * c_score) + (w_content * cnt_score) + (w_pop * p_score)
            p_name = prod_lookup.get(pid, "Unknown")
            cat_name = cat_lookup.get(pid, "General")

            reason = generate_recommendation_reason(
                product_name=p_name,
                category=cat_name,
                collab_score=c_score,
                content_score=cnt_score,
                popularity_score=p_score,
            )

            scored_items.append({
                "product_id": pid,
                "product_name": p_name,
                "category": cat_name,
                "price": price_lookup.get(pid, 0.0),
                "score": round(float(final_score), 4),
                "component_scores": {
                    "collaborative": round(float(c_score), 4),
                    "content": round(float(cnt_score), 4),
                    "popularity": round(float(p_score), 4),
                },
                "reason": reason,
            })

        # Sort and take top_k
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        return scored_items[:top_k]
