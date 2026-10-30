"""
src/recommendation/evaluation.py
Time-aware offline evaluation of recommendation engines.
Calculates Precision@K, Recall@K, MAP@K and NDCG@K for four models.

Leakage control: the test window starts at a cut-off timestamp. Every model is fit only on history
strictly before that cut-off, including the popularity statistics and the product-review ratings.
"""
import json
from typing import Any, Dict, List, Set

import numpy as np
import pandas as pd

from src.features.interaction_matrix import split_interactions_chronologically
from src.recommendation.collaborative import CollaborativeRecommender
from src.recommendation.content_based import ContentBasedRecommender
from src.recommendation.hybrid import HybridRecommender
from src.recommendation.popularity import PopularityRecommender
from src.utils.config import METRICS_FILE, PROCESSED_DATA_DIR, RANDOM_SEED, ensure_directories
from src.utils.logging import get_logger

logger = get_logger("recommendation_evaluation")


def precision_at_k(recommended: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculate Precision@K."""
    if k == 0 or not recommended:
        return 0.0
    hits = sum(1 for item in recommended[:k] if item in ground_truth)
    return hits / float(k)


def recall_at_k(recommended: List[str], ground_truth: Set[str], k: int) -> float:
    """Calculate Recall@K."""
    if not ground_truth or not recommended:
        return 0.0
    hits = sum(1 for item in recommended[:k] if item in ground_truth)
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
    dcg = sum(1.0 / np.log2(i + 2) for i, p in enumerate(recommended[:k]) if p in ground_truth)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(ground_truth), k)))
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def build_rationale(winner: str, metrics_table: Dict[str, Dict[str, float]], n_users: int) -> str:
    """Describe the result using only the computed numbers."""
    ranking = sorted(metrics_table.items(), key=lambda kv: kv[1]["NDCG@10"], reverse=True)
    scores = "; ".join(f"{name} {vals['NDCG@10']:.4f}" for name, vals in ranking)
    return (
        f"{winner} has the highest NDCG@10 on {n_users} held-out customers. "
        f"NDCG@10 by model: {scores}."
    )


def evaluate_models_chronological(
    interactions_df: pd.DataFrame = None,
    products_df: pd.DataFrame = None,
    transactions_df: pd.DataFrame = None,
    reviews_df: pd.DataFrame = None,
    sample_users: int = 400,
) -> Dict[str, Any]:
    """Run offline evaluation of all four models on a chronological test window."""
    ensure_directories()
    if interactions_df is None:
        interactions_df = pd.read_csv(PROCESSED_DATA_DIR / "interactions.csv")
        products_df = pd.read_csv(PROCESSED_DATA_DIR / "products.csv")
        transactions_df = pd.read_csv(PROCESSED_DATA_DIR / "transactions.csv")
        reviews_df = pd.read_csv(PROCESSED_DATA_DIR / "reviews.csv")

    logger.info("Splitting interactions chronologically (80% train, 20% test)...")
    train_inter, test_inter = split_interactions_chronologically(interactions_df, test_ratio=0.20)

    # Cut-off: nothing at or after the first test event may inform any model.
    cutoff = pd.to_datetime(test_inter["timestamp"]).min()
    train_tx = transactions_df[pd.to_datetime(transactions_df["transaction_date"]) < cutoff]
    train_reviews = reviews_df[pd.to_datetime(reviews_df["review_date"]) < cutoff]
    logger.info(
        f"Training history: {len(train_tx)} transactions and {len(train_reviews)} reviews before {cutoff}."
    )

    # Ground truth: products bought, carted or wishlisted in the test window.
    high_intent = test_inter[test_inter["interaction_type"].isin(["purchase", "cart", "wishlist"])]
    ground_truth = high_intent.groupby("customer_id")["product_id"].apply(set).to_dict()

    eval_users = sorted(u for u, items in ground_truth.items() if len(items) >= 1)
    rng = np.random.default_rng(RANDOM_SEED)
    if len(eval_users) > sample_users:
        eval_users = sorted(rng.choice(eval_users, size=sample_users, replace=False).tolist())

    logger.info(f"Evaluating models across {len(eval_users)} active test customers...")

    pop_engine = PopularityRecommender().fit(train_tx, products_df, train_reviews)
    content_engine = ContentBasedRecommender().fit(products_df)
    collab_engine = CollaborativeRecommender(n_factors=25).fit(train_inter, products_df)
    hybrid_engine = HybridRecommender(pop_engine, content_engine, collab_engine)
    hybrid_engine.set_user_history(train_inter)

    user_seen_lookup = train_inter.groupby("customer_id")["product_id"].apply(list).to_dict()

    models_to_test = {
        "Popularity Baseline": lambda uid: [
            r["product_id"]
            for r in pop_engine.recommend(customer_id=uid, top_k=10, exclude_product_ids=user_seen_lookup.get(uid, []))
        ],
        "Content-Based": lambda uid: [
            r["product_id"]
            for r in content_engine.recommend_for_user(
                user_interacted_products=user_seen_lookup.get(uid, []), top_k=10, exclude_seen=True
            )
        ],
        "Collaborative Filtering": lambda uid: [
            r["product_id"] for r in collab_engine.recommend(customer_id=uid, top_k=10, exclude_seen=True)
        ],
        "Hybrid Model": lambda uid: [
            r["product_id"] for r in hybrid_engine.recommend(customer_id=uid, top_k=10, exclude_seen=True)
        ],
    }

    metrics_table: Dict[str, Dict[str, float]] = {}
    for model_name, rec_fn in models_to_test.items():
        p5, p10, r5, r10, ap10, nd10 = [], [], [], [], [], []
        for uid in eval_users:
            gt_items = ground_truth[uid]
            rec_items = rec_fn(uid)
            p5.append(precision_at_k(rec_items, gt_items, k=5))
            p10.append(precision_at_k(rec_items, gt_items, k=10))
            r5.append(recall_at_k(rec_items, gt_items, k=5))
            r10.append(recall_at_k(rec_items, gt_items, k=10))
            ap10.append(average_precision_at_k(rec_items, gt_items, k=10))
            nd10.append(ndcg_at_k(rec_items, gt_items, k=10))

        metrics_table[model_name] = {
            "Precision@5": round(float(np.mean(p5)), 4),
            "Precision@10": round(float(np.mean(p10)), 4),
            "Recall@5": round(float(np.mean(r5)), 4),
            "Recall@10": round(float(np.mean(r10)), 4),
            "MAP@10": round(float(np.mean(ap10)), 4),
            "NDCG@10": round(float(np.mean(nd10)), 4),
        }
        logger.info(
            f"Model '{model_name}': P@10={metrics_table[model_name]['Precision@10']:.4f}, "
            f"R@10={metrics_table[model_name]['Recall@10']:.4f}, NDCG@10={metrics_table[model_name]['NDCG@10']:.4f}"
        )

    winner = max(metrics_table, key=lambda m: metrics_table[m]["NDCG@10"])
    output = {
        "evaluation_type": "Time-Aware Chronological Test Split",
        "training_cutoff": str(cutoff),
        "train_interactions": int(len(train_inter)),
        "test_interactions": int(len(test_inter)),
        "test_users_evaluated": len(eval_users),
        "results_comparison": metrics_table,
        "winning_model": winner,
        "rationale": build_rationale(winner, metrics_table, len(eval_users)),
    }

    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    logger.info(f"Saved recommendation evaluation metrics to: {METRICS_FILE}")
    return output


if __name__ == "__main__":
    evaluate_models_chronological()
