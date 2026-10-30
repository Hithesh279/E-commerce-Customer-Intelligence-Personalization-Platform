"""
api/services/api_service.py
Service layer decoupling FastAPI route handlers from data structures and ML models.
"""
from typing import Any, Dict, List
import joblib
import pandas as pd
from fastapi import HTTPException

from src.analytics.business_metrics import calculate_executive_kpis
from src.analytics.customer_analytics import generate_customer_profile_metrics
from src.analytics.product_analytics import generate_product_performance_metrics
from src.nlp.sentiment_predict import SentimentPredictor
from src.recommendation.hybrid import HybridRecommender
from src.utils.config import (
    MODELS_RECOMMENDATION_DIR,
    MODELS_SENTIMENT_DIR,
    PROCESSED_DATA_DIR,
)
from src.utils.logging import get_logger

logger = get_logger("api_service")


class APIService:
    """Singleton service manager providing fast cached access to datasets and ML models."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIService, cls).__new__(cls)
            cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        """Load datasets and pre-trained models into memory."""
        logger.info("Initializing APIService cache...")
        self.customers_df = pd.read_csv(PROCESSED_DATA_DIR / "customers.csv")
        self.products_df = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")
        self.transactions_df = pd.read_csv(PROCESSED_DATA_DIR / "transactions.csv")
        self.reviews_df = pd.read_csv(PROCESSED_DATA_DIR / "reviews.csv")
        self.interactions_df = pd.read_csv(PROCESSED_DATA_DIR / "interactions.csv")

        # Load aspect observations if present
        aspects_path = PROCESSED_DATA_DIR / "review_aspects.csv"
        self.aspects_df = pd.read_csv(aspects_path) if aspects_path.exists() else pd.DataFrame()

        # Compute executive KPIs, customer profiles, and product performance tables
        self.executive_kpis = calculate_executive_kpis(
            self.customers_df, self.transactions_df, self.reviews_df
        )
        self.customer_profiles = generate_customer_profile_metrics(
            self.customers_df, self.transactions_df, self.reviews_df
        )
        self.product_perf = generate_product_performance_metrics(
            self.products_df, self.transactions_df, self.reviews_df
        )

        # ML Models
        self.sentiment_predictor = SentimentPredictor(model_dir=MODELS_SENTIMENT_DIR)

        pop_path = MODELS_RECOMMENDATION_DIR / "popularity_model.joblib"
        cnt_path = MODELS_RECOMMENDATION_DIR / "content_model.joblib"
        col_path = MODELS_RECOMMENDATION_DIR / "collaborative_model.joblib"

        self.pop_engine = joblib.load(pop_path)
        self.cnt_engine = joblib.load(cnt_path)
        self.collab_engine = joblib.load(col_path)

        self.hybrid_engine = HybridRecommender(self.pop_engine, self.cnt_engine, self.collab_engine)
        self.hybrid_engine.set_user_history(self.interactions_df)
        logger.info("APIService cache fully initialized.")

    def get_executive_kpis(self) -> Dict[str, Any]:
        """Return cached executive business KPIs."""
        return dict(self.executive_kpis)

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Fetch customer profile and behavioral analytics."""
        row = self.customer_profiles[self.customer_profiles["customer_id"] == customer_id]
        if row.empty:
            raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
        return row.iloc[0].to_dict()

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Fetch 360-degree product performance profile."""
        row = self.product_perf[self.product_perf["product_id"] == product_id]
        if row.empty:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")
        p = row.iloc[0]
        return {
            "product_id": str(p["product_id"]),
            "product_name": str(p["product_name"]),
            "category": str(p["category"]),
            "subcategory": str(p.get("subcategory", "")),
            "brand": str(p.get("brand", "")),
            "price": float(p["price"]),
            "total_orders": int(p["total_orders"]),
            "units_sold": int(p["units_sold"]),
            "returned_units": int(p["returned_units"]),
            "gross_revenue": float(p["gross_revenue"]),
            "net_revenue": float(p["net_revenue"]),
            "return_rate": float(p["return_rate"]),
            "review_count": int(p["review_count"]),
            "average_rating": float(p["average_rating"]),
            "positive_sentiment_pct": float(p["positive_sentiment_pct"]),
            "negative_sentiment_pct": float(p["negative_sentiment_pct"]),
            "is_high_sales_low_sentiment": bool(p["is_high_sales_low_sentiment"]),
            "is_low_sales_high_sentiment": bool(p["is_low_sales_high_sentiment"]),
        }

    def get_recommendations(self, customer_id: str, strategy: str = "hybrid", top_k: int = 10) -> Dict[str, Any]:
        """Generate personalized recommendations for a customer using the chosen strategy."""
        # Verify customer exists
        cust_row = self.customers_df[self.customers_df["customer_id"] == customer_id]
        if cust_row.empty:
            raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")

        pref_cat = cust_row.iloc[0]["preferred_category"]

        if strategy.lower() == "collaborative":
            recs = self.collab_engine.recommend(customer_id, top_k=top_k)
            if not recs:
                recs = self.pop_engine.recommend(customer_id, category=pref_cat, top_k=top_k)
        elif strategy.lower() == "content":
            history = self.hybrid_engine.user_history.get(customer_id, [])
            recs = self.cnt_engine.recommend_for_user(history, top_k=top_k)
            if not recs:
                recs = self.pop_engine.recommend(customer_id, category=pref_cat, top_k=top_k)
        elif strategy.lower() == "popularity":
            recs = self.pop_engine.recommend(customer_id, category=pref_cat, top_k=top_k)
        else:
            strategy = "hybrid"
            recs = self.hybrid_engine.recommend(customer_id, top_k=top_k, preferred_category=pref_cat)

        return {
            "customer_id": customer_id,
            "model_strategy": strategy,
            "count": len(recs),
            "recommendations": recs,
        }

    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find catalog items similar to product_id."""
        prod = self.products_df[self.products_df["product_id"] == product_id]
        if prod.empty:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")

        return self.cnt_engine.recommend_similar_products(product_id, top_k=top_k)

    def analyze_review(self, text: str) -> Dict[str, Any]:
        """Classify sentiment and extract 11 product aspects."""
        sent_res = self.sentiment_predictor.predict(text)
        return {
            "text": text,
            "sentiment": sent_res["sentiment"],
            "confidence": sent_res["confidence"],
            "probabilities": sent_res["probabilities"],
            "aspects": sent_res.get("aspects", []),
        }

    def get_product_sentiment(self, product_id: str) -> Dict[str, Any]:
        """Get product sentiment score, review volume, and top aspect sentiments."""
        row = self.product_perf[self.product_perf["product_id"] == product_id]
        if row.empty:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")

        p = row.iloc[0]
        top_aspects = []
        if not self.aspects_df.empty:
            p_aspects = self.aspects_df[self.aspects_df["product_id"] == product_id]
            if not p_aspects.empty:
                agg = p_aspects.groupby("aspect").agg(
                    mentions=("review_id", "count"),
                    avg_score=("sentiment_score", "mean"),
                ).reset_index()
                agg["avg_score"] = agg["avg_score"].round(3)
                top_aspects = agg.to_dict(orient="records")

        return {
            "product_id": product_id,
            "product_name": p["product_name"],
            "category": p["category"],
            "review_count": int(p["review_count"]),
            "average_rating": float(p["average_rating"]),
            "positive_sentiment_pct": float(p["positive_sentiment_pct"]),
            "negative_sentiment_pct": float(p["negative_sentiment_pct"]),
            "top_aspects": top_aspects,
        }


def get_api_service() -> APIService:
    """Factory dependency returning APIService singleton."""
    return APIService()
