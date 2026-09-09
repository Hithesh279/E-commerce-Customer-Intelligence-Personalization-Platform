"""
src/nlp/sentiment_predict.py
Inference module for review sentiment classification with confidence scoring.
"""
from typing import Dict, List, Union
import joblib
import numpy as np

from src.nlp.preprocessing import clean_text
from src.utils.config import MODELS_SENTIMENT_DIR
from src.utils.logging import get_logger

logger = get_logger("sentiment_predict")


class SentimentPredictor:
    """Predictor class for review sentiment inference."""

    def __init__(self, model_dir=None):
        self.model_dir = model_dir or MODELS_SENTIMENT_DIR
        self.model_path = self.model_dir / "model.joblib"
        self.vec_path = self.model_dir / "vectorizer.joblib"
        self.model = None
        self.vectorizer = None
        self._load()

    def _load(self) -> None:
        """Load serialized model and vectorizer from disk."""
        if not self.model_path.exists() or not self.vec_path.exists():
            raise FileNotFoundError(
                f"Sentiment model artifacts missing in {self.model_dir}. Please run sentiment training first."
            )
        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vec_path)
        logger.info("Successfully loaded sentiment model artifacts.")

    def predict(self, text: str) -> Dict[str, Union[str, float, Dict[str, float], List]]:
        """
        Predict sentiment label, confidence score, and class probabilities for a single text.
        Calibrates with fine-grained aspect polarity when aspects are present.
        """
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "sentiment": "Neutral",
                "confidence": 0.3333,
                "probabilities": {"Negative": 0.3333, "Neutral": 0.3334, "Positive": 0.3333},
                "aspects": [],
            }

        cleaned = clean_text(text)
        features = self.vectorizer.transform([cleaned])
        probas = self.model.predict_proba(features)[0]
        classes = self.model.classes_

        # Aspect-aware calibration
        from src.nlp.aspect_extraction import extract_aspect_sentiment_from_text
        aspects = extract_aspect_sentiment_from_text(text)

        if aspects:
            pos_count = sum(1 for a in aspects if a["sentiment"] == "Positive")
            neg_count = sum(1 for a in aspects if a["sentiment"] == "Negative")

            prob_map = dict(zip(classes, probas))
            if neg_count > pos_count:
                shift = min(0.20, 0.08 * (neg_count - pos_count))
                prob_map["Negative"] = min(0.99, prob_map.get("Negative", 0.0) + shift)
                prob_map["Positive"] = max(0.005, prob_map.get("Positive", 0.0) - shift)
            elif pos_count > neg_count:
                shift = min(0.20, 0.08 * (pos_count - neg_count))
                prob_map["Positive"] = min(0.99, prob_map.get("Positive", 0.0) + shift)
                prob_map["Negative"] = max(0.005, prob_map.get("Negative", 0.0) - shift)

            total_p = sum(prob_map.values())
            probas = np.array([prob_map[c] / total_p for c in classes])

        pred_idx = np.argmax(probas)
        predicted_class = classes[pred_idx]
        confidence = float(probas[pred_idx])

        prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(classes, probas)}

        return {
            "sentiment": predicted_class,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "aspects": aspects,
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Union[str, float]]]:
        """Predict sentiment for a batch of texts efficiently."""
        cleaned_list = [clean_text(t) for t in texts]
        features = self.vectorizer.transform(cleaned_list)
        probas = self.model.predict_proba(features)
        classes = self.model.classes_

        results = []
        for p in probas:
            idx = np.argmax(p)
            results.append({
                "sentiment": classes[idx],
                "confidence": round(float(p[idx]), 4),
            })
        return results
