"""
src/nlp/sentiment_train.py
Trains and evaluates sentiment analysis models (TF-IDF + Logistic Regression & Naive Bayes).
Saves serialized artifacts and real evaluation metrics.
"""
import json
from pathlib import Path
from typing import Any, Dict, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.ensemble import VotingClassifier

from src.nlp.preprocessing import clean_text
from src.utils.config import (
    MODELS_SENTIMENT_DIR,
    PROCESSED_DATA_DIR,
    RANDOM_SEED,
    ensure_directories,
)
from src.utils.logging import get_logger

logger = get_logger("sentiment_train")


def assign_sentiment_label(rating: int) -> str:
    """Map 1-5 star ratings to discrete sentiment classes."""
    if rating <= 2:
        return "Negative"
    elif rating == 3:
        return "Neutral"
    else:
        return "Positive"


def train_sentiment_models(
    reviews_df: pd.DataFrame = None,
) -> Tuple[LogisticRegression, TfidfVectorizer, Dict[str, Any]]:
    """
    Train TF-IDF + Logistic Regression sentiment classifier with Naive Bayes baseline.
    Avoids data leakage by fitting vectorizer strictly on training partition.
    """
    ensure_directories()
    if reviews_df is None:
        from src.utils.config import RAW_DATA_DIR
        rw_path = RAW_DATA_DIR / "real_world_reviews.csv"
        if rw_path.exists():
            reviews_df = pd.read_csv(rw_path)
            logger.info(f"Loaded {len(reviews_df)} authentic real-world reviews from internet dataset ({rw_path}).")
        else:
            reviews_path = PROCESSED_DATA_DIR / "reviews.csv"
            reviews_df = pd.read_csv(reviews_path)
            logger.info(f"Loaded {len(reviews_df)} reviews from {reviews_path}.")
    df = reviews_df.copy()
    df["sentiment"] = df["rating"].apply(assign_sentiment_label)
    df["cleaned_text"] = df["review_text"].apply(lambda t: clean_text(t, remove_stopwords=False))

    # Stratified Train/Test Split
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_SEED,
        stratify=df["sentiment"],
    )

    logger.info(f"Split: Train = {len(train_df)} reviews, Test = {len(test_df)} reviews.")

    # Fit TF-IDF Vectorizer strictly on train split with unigrams and bigrams
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=12000,
        min_df=1,
        sublinear_tf=True,
        strip_accents="unicode",
    )
    X_train = vectorizer.fit_transform(train_df["cleaned_text"])
    X_test = vectorizer.transform(test_df["cleaned_text"])
    y_train = train_df["sentiment"].values
    y_test = test_df["sentiment"].values

    classes = ["Negative", "Neutral", "Positive"]

    # 1. Base Model 1: Tuned L2-regularized Logistic Regression
    lr = LogisticRegression(
        C=3.5,
        max_iter=1000,
        random_state=RANDOM_SEED,
    )
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)

    # 2. Base Model 2: Multinomial Naive Bayes
    nb = MultinomialNB(alpha=0.3)
    nb.fit(X_train, y_train)
    nb_pred = nb.predict(X_test)
    nb_acc = accuracy_score(y_test, nb_pred)

    # 3. Base Model 3: Complement Naive Bayes (handles class imbalance)
    cnb = ComplementNB(alpha=0.4)
    cnb.fit(X_train, y_train)
    cnb_pred = cnb.predict(X_test)
    cnb_acc = accuracy_score(y_test, cnb_pred)

    # 4. Primary Production Model: Soft Voting Ensemble Classifier
    ensemble = VotingClassifier(
        estimators=[
            ("lr", lr),
            ("nb", nb),
            ("cnb", cnb),
        ],
        voting="soft",
        weights=[1, 2, 1],
    )
    ensemble.fit(X_train, y_train)
    y_pred = ensemble.predict(X_test)
    ens_acc = accuracy_score(y_test, y_pred)

    # Evaluation Metrics calculation
    ens_report = classification_report(y_test, y_pred, labels=classes, output_dict=True)
    ens_cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()

    logger.info(f"Production Soft Voting Ensemble Accuracy: {ens_acc:.4f}")
    logger.info(f"Logistic Regression Accuracy: {lr_acc:.4f}")
    logger.info(f"Multinomial Naive Bayes Accuracy: {nb_acc:.4f}")
    logger.info(f"Complement Naive Bayes Accuracy: {cnb_acc:.4f}")

    evaluation_results = {
        "model_type": "Soft Voting Ensemble (Logistic Regression + MultinomialNB + ComplementNB)",
        "baseline_model": "Multinomial Naive Bayes",
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "accuracy": round(ens_acc, 4),
        "baseline_accuracy": round(nb_acc, 4),
        "logistic_regression_accuracy": round(lr_acc, 4),
        "complement_nb_accuracy": round(cnb_acc, 4),
        "classes": classes,
        "classification_report": ens_report,
        "confusion_matrix": ens_cm,
    }

    # Save artifacts
    model_path = MODELS_SENTIMENT_DIR / "model.joblib"
    vec_path = MODELS_SENTIMENT_DIR / "vectorizer.joblib"
    metrics_path = MODELS_SENTIMENT_DIR / "sentiment_metrics.json"

    joblib.dump(ensemble, model_path)
    joblib.dump(vectorizer, vec_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_results, f, indent=2)

    logger.info(f"Saved optimized sentiment artifacts to {MODELS_SENTIMENT_DIR}")
    return ensemble, vectorizer, evaluation_results


if __name__ == "__main__":
    train_sentiment_models()
