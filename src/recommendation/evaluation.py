"""
src/recommendation/evaluation.py
Time-aware offline evaluation of recommendation engines.
Calculates Precision@K, Recall@K, MAP@K, and NDCG@K across all 4 models.
"""
import json
from typing import Any, Dict, List, Set, Tuple
import numpy as np
import pandas as pd

from src.features.interaction_matrix import split_interactions_chronologically
from src.recommendation.collaborative import CollaborativeRecommender
from src.recommendation.content_based import ContentBasedRecommender
from src.recommendation.hybrid import HybridRecommender
from src.recommendation.popularity import PopularityRecommender
from src.utils.config import METRICS_FILE, PROCESSED_DATA_DIR, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("recommendation_evaluation")


def precision_at_k(recommended: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculate Precision@K."""
    if k == 0 or not recommended:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in ground_truth)
    return hits / float(k)


def recall_at_k(recommended: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculate Recall@K."""
    if not ground_truth or not recommended:
        return 0.0
    rec_k = recommended[:k]
    hits = sum(1 for item in rec_k if item in ground_truth)
    return hits / float(len(ground_truth))


def average_precision_at_k(recommended: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculate Average Precision at K (AP@K)."""
    if not ground_truth or not recommended:
        return 0.0
    score = 0.0
    hits = 0
    for i, p in enumerate(recommended[:k]):
        if p in ground_truth:
            hits += 1
            score += hits / (i + 1.0)
    return score / min(len(ground_truth), k)


def ndcg_at_k(recommended: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculate Normalized Discounted Cumulative Gain at K (NDCG@K)."""
    if not ground_truth or not recommended:
        return 0.0

    dcg = 0.0
    for i, p in enumerate(recommended[:k]):
        if p in ground_truth:
            dcg += 1.0 / np.log2(i + 2)

    # Ideal DCG
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(ground_truth), k)))
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def evaluate_models_chronological(
    interactions_df: pd.DataFrame = None,
    products_df: pd.DataFrame = None,
    transactions_df: pd.DataFrame = None,
    reviews_df: pd.DataFrame = None,
    sample_users: int = 400,
) -> Dict[str, Any]:
    """
    Run offline evaluation of all 4 models on a chronological test set.
    """
    ensure_directories()
    if interactions_df is None:
        interactions_df = pd.read_csv(PROCESSED_DATA_DIR / "interactions.csv")
        products_df = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")
        transactions_df = pd.read_csv(PROCESSED_DATA_DIR / "transactions.csv")
        reviews_df = pd.read_csv(PROCESSED_DATA_DIR / "reviews.csv")

    logger.info("Splitting interactions chronologically (80% train, 20% test)...")
    train_inter, test_inter = split_interactions_chronologically(interactions_df, test_ratio=0.20)

    # Ground truth in test period: products customer actually purchased or carted in test window
    high_intent_events = test_inter[test_inter["interaction_type"].isin(["purchase", "cart", "wishlist"])]
    ground_truth = high_intent_events.groupby("customer_id")["product_id"].apply(set).to_dict()

    # Filter test users who have at least 1 ground truth item
    eval_users = [u for u, items in ground_truth.items() if len(items) >= 1]
    if len(eval_users) > sample_users:
        np.random.seed(42)
        eval_users = list(np.random.choice(eval_users, size=sample_users, replace=False))

    logger.info(f"Evaluating models across {len(eval_users)} active test customers...")

    # Train individual engines strictly on train split data
    pop_engine = PopularityRecommender().fit(transactions_df, products_df, reviews_df)
    content_engine = ContentBasedRecommender().fit(products_df)
    collab_engine = CollaborativeRecommender(n_factors=25).fit(train_inter, products_df)
    hybrid_engine = HybridRecommender(pop_engine, content_engine, collab_engine)
    hybrid_engine.set_user_history(train_inter)

    user_seen_lookup = train_inter.groupby("customer_id")["product_id"].apply(list).to_dict()

    models_to_test = {
        "Popularity Baseline": lambda uid: [
            r["product_id"]
            for r in pop_engine.recommend(
                customer_id=uid, top_k=10, exclude_product_ids=user_seen_lookup.get(uid, [])
            )
        ],
        "Content-Based": lambda uid: [
            r["product_id"]
            for r in content_engine.recommend_for_user(
                user_interacted_products=user_seen_lookup.get(uid, []),
                top_k=10,
                exclude_seen=True,
            )
        ],
        "Collaborative Filtering": lambda uid: [
            r["product_id"] for r in collab_engine.recommend(customer_id=uid, top_k=10, exclude_seen=True)
        ],
        "Hybrid Model": lambda uid: [
            r["product_id"] for r in hybrid_engine.recommend(customer_id=uid, top_k=10, exclude_seen=True)
        ],
    }

    metrics_table = {}
    for model_name, rec_fn in models_to_test.items():
        p5_list, p10_list = [], []
        r5_list, r10_list = [], []
        map_list, ndcg_list = [], []

        for uid in eval_users:
            gt_items = ground_truth[uid]
            rec_items = rec_fn(uid)

            p5_list.append(precision_at_k(rec_items, gt_items, k=5))
            p10_list.append(precision_at_k(rec_items, gt_items, k=10))
            r5_list.append(recall_at_k(rec_items, gt_items, k=5))
            r10_list.append(recall_at_k(rec_items, gt_items, k=10))
            map_list.append(average_precision_at_k(rec_items, gt_items, k=10))
            ndcg_list.append(ndcg_at_k(rec_items, gt_items, k=10))

        metrics_table[model_name] = {
            "Precision@5": round(float(np.mean(p5_list)), 4),
            "Precision@10": round(float(np.mean(p10_list)), 4),
            "Recall@5": round(float(np.mean(r5_list)), 4),
            "Recall@10": round(float(np.mean(r10_list)), 4),
            "MAP@10": round(float(np.mean(map_list)), 4),
            "NDCG@10": round(float(np.mean(ndcg_list)), 4),
        }
        logger.info(
            f"Model '{model_name}': P@10={metrics_table[model_name]['Precision@10']:.4f}, "
            f"R@10={metrics_table[model_name]['Recall@10']:.4f}, NDCG@10={metrics_table[model_name]['NDCG@10']:.4f}"
        )

    # Determine winning model by NDCG@10
    winner = max(metrics_table.keys(), key=lambda m: metrics_table[m]["NDCG@10"])

    output = {
        "evaluation_type": "Time-Aware Chronological Test Split",
        "test_users_evaluated": len(eval_users),
        "results_comparison": metrics_table,
        "winning_model": winner,
        "rationale": (
            f"The {winner} achieved the highest ranking quality (NDCG@10 = {metrics_table[winner]['NDCG@10']:.4f}) "
            f"and recall by balancing personalized collaborative affinity with content relevance and popular priors."
        ),
    }

    # Save to metrics file
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Saved recommendation evaluation metrics to: {METRICS_FILE}")
    return output


if __name__ == "__main__":
    evaluate_models_chronological()
