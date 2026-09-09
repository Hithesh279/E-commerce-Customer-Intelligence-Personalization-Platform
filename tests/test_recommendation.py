"""
tests/test_recommendation.py
Tests for recommendation models, cold-start handling, and ranking outputs.
"""
import joblib
import pytest
from src.recommendation.hybrid import HybridRecommender
from src.utils.config import MODELS_RECOMMENDATION_DIR


@pytest.fixture
def recommender_bundle():
    pop = joblib.load(MODELS_RECOMMENDATION_DIR / "popularity_model.joblib")
    cnt = joblib.load(MODELS_RECOMMENDATION_DIR / "content_model.joblib")
    col = joblib.load(MODELS_RECOMMENDATION_DIR / "collaborative_model.joblib")
    hybrid = HybridRecommender(pop, cnt, col)
    return {"pop": pop, "cnt": cnt, "col": col, "hybrid": hybrid}


def test_popularity_recommender_returns_top_k(recommender_bundle):
    pop = recommender_bundle["pop"]
    recs = pop.recommend(top_k=5)
    assert len(recs) == 5
    assert "product_id" in recs[0]
    assert "score" in recs[0]
    assert recs[0]["score"] >= recs[-1]["score"]


def test_content_recommender_similar_products(recommender_bundle):
    cnt = recommender_bundle["cnt"]
    recs = cnt.recommend_similar_products("PROD_0001", top_k=4)
    assert len(recs) == 4
    # Ensure source product is excluded
    assert all(r["product_id"] != "PROD_0001" for r in recs)


def test_hybrid_recommender_cold_start_handling(recommender_bundle):
    hybrid = recommender_bundle["hybrid"]
    # Pass unseen customer ID (cold start)
    recs = hybrid.recommend(customer_id="CUST_UNSEEN_99999", top_k=5)
    assert len(recs) == 5
    assert all("reason" in r for r in recs)
