"""
run_pipeline.py
Single orchestrator script to execute the complete end-to-end data science pipeline:
Data Generation -> Cleaning -> Feature Engineering -> NLP Sentiment & ABSA ->
Topic Modeling -> Recommender Training -> Offline Evaluation -> Database & Power BI Export.
"""
import time
from src.data.cleaning import run_cleaning_pipeline
from src.data.ingestion import generate_and_save_dataset
from src.database.db_manager import setup_database_and_export
from src.nlp.aspect_extraction import process_reviews_absa
from src.nlp.sentiment_train import train_sentiment_models
from src.nlp.topic_modeling import train_topic_model
from src.recommendation.evaluation import evaluate_models_chronological
from src.recommendation.train import train_and_save_recommenders
from src.utils.logging import get_logger

logger = get_logger("run_pipeline")


def run_full_pipeline():
    """Execute all pipeline phases sequentially with detailed progress logging."""
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("STARTING END-TO-END E-COMMERCE CUSTOMER INTELLIGENCE PIPELINE")
    logger.info("=" * 70)

    # 1. Data Generation
    logger.info("\n>>> Phase 1: Synthetic Data Generation with Controlled Anomalies...")
    generate_and_save_dataset()

    # 2. Data Cleaning
    logger.info("\n>>> Phase 2: Data Cleaning & Preprocessing Pipeline...")
    run_cleaning_pipeline()

    # 3. NLP Sentiment Analysis
    logger.info("\n>>> Phase 3: NLP Review Sentiment Model Training...")
    train_sentiment_models()

    # 4. Aspect-Based Sentiment Analysis (ABSA)
    logger.info("\n>>> Phase 4: Aspect-Based Sentiment Analysis (11 Product Aspects)...")
    process_reviews_absa()

    # 5. Topic Modeling
    logger.info("\n>>> Phase 5: NMF Topic & Recurring Complaint Discovery...")
    train_topic_model()

    # 6. Recommendation Model Training
    logger.info("\n>>> Phase 6: Recommendation Engines Training & Serialization...")
    train_and_save_recommenders()

    # 7. Recommendation Offline Evaluation
    logger.info("\n>>> Phase 7: Time-Aware Offline Recommender Evaluation...")
    eval_results = evaluate_models_chronological()

    # 8. Relational Database & Power BI Export
    logger.info("\n>>> Phase 8: SQLite Database Setup & Power BI Star-Schema Export...")
    setup_database_and_export()

    elapsed = time.time() - start_time
    logger.info("=" * 70)
    logger.info(f"PIPELINE SUCCESSFULLY COMPLETED IN {elapsed:.1f} SECONDS")
    logger.info(f"Winning Recommendation Strategy: {eval_results.get('winning_model')}")
    logger.info("=" * 70)


if __name__ == "__main__":
    run_full_pipeline()
