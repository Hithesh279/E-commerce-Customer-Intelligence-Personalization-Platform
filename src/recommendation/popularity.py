"""
src/recommendation/popularity.py
Popularity baseline recommender based on sales volume, rating weight, and recency decay.
"""
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger("popularity_recommender")


class PopularityRecommender:
    """Popularity-based baseline recommendation engine."""

    def __init__(self):
        self.popular_products: pd.DataFrame = pd.DataFrame()
        self.category_popular: Dict[str, pd.DataFrame] = {}

    def fit(self, transactions_df: pd.DataFrame, products_df: pd.DataFrame, reviews_df: pd.DataFrame) -> "PopularityRecommender":
        """
        Fit popularity scores combining sales volume, rating, and return penalty.
        """
        # Exclude returns
        completed = transactions_df[transactions_df["return_status"] != "Returned"]
        sales_vol = completed.groupby("product_id")["quantity"].sum().rename("units_sold")
        order_cnt = completed.groupby("product_id")["transaction_id"].count().rename("order_count")

        # Ratings
        ratings = reviews_df.groupby("product_id")["rating"].mean().rename("avg_rating")
        rev_cnt = reviews_df.groupby("product_id")["review_id"].count().rename("rev_count")

        pop_df = products_df[["product_id", "product_name", "category", "price"]].copy()
        pop_df = pop_df.merge(sales_vol, on="product_id", how="left").fillna({"units_sold": 0})
        pop_df = pop_df.merge(order_cnt, on="product_id", how="left").fillna({"order_count": 0})
        pop_df = pop_df.merge(ratings, on="product_id", how="left").fillna({"avg_rating": 3.0})
        pop_df = pop_df.merge(rev_cnt, on="product_id", how="left").fillna({"rev_count": 0})

        # Bayesian smoothed rating score
        global_avg_rating = float(reviews_df["rating"].mean())
        m = 5  # minimum reviews weight
        pop_df["bayesian_rating"] = (
            (pop_df["rev_count"] * pop_df["avg_rating"] + m * global_avg_rating)
            / (pop_df["rev_count"] + m)
        )

        # Composite Popularity Score: normalized units sold * bayesian rating
        max_units = max(pop_df["units_sold"].max(), 1)
        pop_df["popularity_score"] = (
            (pop_df["units_sold"] / max_units) * 0.7 + (pop_df["bayesian_rating"] / 5.0) * 0.3
        ).round(4)

        self.popular_products = pop_df.sort_values("popularity_score", ascending=False).reset_index(drop=True)

        # Cache category popular
        for cat, group in self.popular_products.groupby("category"):
            self.category_popular[cat] = group.reset_index(drop=True)

        logger.info(f"Fitted popularity recommender for {len(self.popular_products)} products.")
        return self

    def recommend(
        self,
        customer_id: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 10,
        exclude_product_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Return top-K popular products globally or by category."""
        exclude = set(exclude_product_ids or [])
        df = self.category_popular.get(category, self.popular_products) if category else self.popular_products

        filtered = df[~df["product_id"].isin(exclude)]
        top_df = filtered.head(top_k)

        results = []
        for _, row in top_df.iterrows():
            results.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "price": row["price"],
                "score": float(row["popularity_score"]),
                "reason": f"Trending top-seller in {row['category']} ({row['avg_rating']:.1f}★ rating)",
            })
        return results
