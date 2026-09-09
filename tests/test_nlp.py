"""
tests/test_nlp.py
Tests for review NLP preprocessing and sentiment prediction.
"""
from src.nlp.preprocessing import clean_text, expand_contractions
from src.nlp.sentiment_predict import SentimentPredictor


def test_expand_contractions():
    raw = "I haven't seen this, it won't work and can't happen."
    expanded = expand_contractions(raw)
    assert "have not" in expanded
    assert "will not" in expanded
    assert "cannot" in expanded


def test_clean_text():
    raw = "AMAZING product!! https://example.com/test #awesome 123"
    cleaned = clean_text(raw, remove_stopwords=False)
    assert "http" not in cleaned
    assert "amazing product" in cleaned


def test_sentiment_predictor_inference():
    predictor = SentimentPredictor()
    res = predictor.predict("The product is absolutely amazing, outstanding quality and fast delivery.")

    assert res["sentiment"] in ["Positive", "Neutral", "Negative"]
    assert 0.0 <= res["confidence"] <= 1.0
    assert "Positive" in res["probabilities"]
    assert res["probabilities"]["Positive"] > res["probabilities"]["Negative"]


def test_sentiment_predictor_empty_string():
    predictor = SentimentPredictor()
    res = predictor.predict("")
    assert res["sentiment"] == "Neutral"
