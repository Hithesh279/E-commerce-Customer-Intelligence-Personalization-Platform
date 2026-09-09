"""
tests/test_aspects.py
Tests for Aspect-Based Sentiment Analysis (ABSA).
"""
from src.nlp.aspect_extraction import extract_aspect_sentiment_from_text


def test_aspect_extraction_compound_review():
    text = "The battery lasts all day, but the camera quality is disappointing."
    aspects = extract_aspect_sentiment_from_text(text)

    aspect_names = {a["aspect"] for a in aspects}
    assert "battery" in aspect_names
    assert "camera" in aspect_names

    battery_item = next(a for a in aspects if a["aspect"] == "battery")
    camera_item = next(a for a in aspects if a["aspect"] == "camera")

    assert battery_item["sentiment"] == "Positive"
    assert battery_item["sentiment_score"] > 0
    assert camera_item["sentiment"] == "Negative"
    assert camera_item["sentiment_score"] < 0


def test_aspect_extraction_pricing_and_delivery():
    text = "Super fast delivery, however the price was heavily overpriced."
    aspects = extract_aspect_sentiment_from_text(text)

    aspect_map = {a["aspect"]: a["sentiment"] for a in aspects}
    assert aspect_map.get("delivery") == "Positive"
    assert aspect_map.get("price") == "Negative"


def test_aspect_extraction_empty_text():
    assert extract_aspect_sentiment_from_text("") == []
