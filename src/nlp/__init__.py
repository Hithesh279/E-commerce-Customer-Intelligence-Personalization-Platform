"""
src/nlp package.
"""
from src.nlp.aspect_extraction import (
    aggregate_aspect_metrics,
    extract_aspect_sentiment_from_text,
    process_reviews_absa,
)
from src.nlp.preprocessing import clean_text, clean_text_series
from src.nlp.sentiment_predict import SentimentPredictor
from src.nlp.sentiment_train import train_sentiment_models
from src.nlp.topic_modeling import train_topic_model

__all__ = [
    "clean_text",
    "clean_text_series",
    "train_sentiment_models",
    "SentimentPredictor",
    "extract_aspect_sentiment_from_text",
    "process_reviews_absa",
    "aggregate_aspect_metrics",
    "train_topic_model",
]
