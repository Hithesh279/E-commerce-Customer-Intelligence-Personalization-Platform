"""
app/services/inference_service.py
Cached model loading and inference service for Streamlit application.
Loads pre-trained artifacts directly without retraining on startup.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import pandas as pd
import streamlit as st

from src.nlp.aspect_extraction import extract_aspect_sentiment_from_text
from src.nlp.sentiment_predict import SentimentPredictor
from src.recommendation.hybrid import HybridRecommender
from src.utils.config import (
    MODELS_RECOMMENDATION_DIR,
    MODELS_SENTIMENT_DIR,
    PROCESSED_DATA_DIR,
)


@st.cache_resource(show_spinner=False)
def load_sentiment_predictor() -> SentimentPredictor:
    """Load cached sentiment prediction engine."""
    return SentimentPredictor(model_dir=MODELS_SENTIMENT_DIR)


@st.cache_resource(show_spinner=False)
def load_recommendation_system():
    """Load cached recommendation models and hybrid engine."""
    pop_path = MODELS_RECOMMENDATION_DIR / "popularity_model.joblib"
    cnt_path = MODELS_RECOMMENDATION_DIR / "content_model.joblib"
    col_path = MODELS_RECOMMENDATION_DIR / "collaborative_model.joblib"

    if not pop_path.exists() or not cnt_path.exists() or not col_path.exists():
        raise FileNotFoundError("Recommendation model artifacts missing. Please run model training first.")

    pop_engine = joblib.load(pop_path)
    cnt_engine = joblib.load(cnt_path)
    collab_engine = joblib.load(col_path)

    hybrid_engine = HybridRecommender(pop_engine, cnt_engine, collab_engine)

    # Load interaction history
    interactions_df = pd.read_csv(PROCESSED_DATA_DIR / "interactions.csv")
    hybrid_engine.set_user_history(interactions_df)

    return {
        "popularity": pop_engine,
        "content": cnt_engine,
        "collaborative": collab_engine,
        "hybrid": hybrid_engine,
    }


def analyze_review_text(text: str) -> Dict[str, Any]:
    """Analyze a customer review: sentiment, confidence, probabilities, and aspect sentiments."""
    predictor = load_sentiment_predictor()
    sent_res = predictor.predict(text)
    aspects = extract_aspect_sentiment_from_text(text)

    return {
        "text": text,
        "sentiment": sent_res["sentiment"],
        "confidence": sent_res["confidence"],
        "probabilities": sent_res["probabilities"],
        "aspects": aspects,
    }
