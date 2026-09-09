"""
src/features/interaction_matrix.py
Builds weighted implicit customer-product interaction matrices and chronological train/test splits.
"""
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from src.utils.config import INTERACTION_WEIGHTS, RANDOM_SEED
from src.utils.logging import get_logger

logger = get_logger("interaction_matrix")


def split_interactions_chronologically(
    interactions_df: pd.DataFrame,
    test_ratio: float = 0.20,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split interaction events chronologically to prevent temporal data leakage.

    Parameters
    ----------
    interactions_df : pd.DataFrame
        Interaction event stream.
    test_ratio : float
        Fraction of events allocated to the test set (most recent).

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (train_df, test_df)
    """
    sorted_df = interactions_df.sort_values("timestamp").reset_index(drop=True)
    split_idx = int(len(sorted_df) * (1.0 - test_ratio))
    train_df = sorted_df.iloc[:split_idx].copy()
    test_df = sorted_df.iloc[split_idx:].copy()

    logger.info(
        f"Chronological split: Train = {len(train_df)} events "
        f"({train_df['timestamp'].min()} to {train_df['timestamp'].max()}), "
        f"Test = {len(test_df)} events "
        f"({test_df['timestamp'].min()} to {test_df['timestamp'].max()})"
    )
    return train_df, test_df


def build_interaction_matrix(
    interactions_df: pd.DataFrame,
    weights_map: Dict[str, float] = None,
) -> Tuple[csr_matrix, Dict[str, int], Dict[int, str], Dict[str, int], Dict[int, str]]:
    """
    Aggregate interactions into a weighted user-item sparse CSR matrix.

    Returns
    -------
    Tuple containing:
        - csr_matrix: shape (n_users, n_items)
        - user_to_idx: dict mapping customer_id -> row index
        - idx_to_user: dict mapping row index -> customer_id
        - item_to_idx: dict mapping product_id -> col index
        - idx_to_item: dict mapping col index -> product_id
    """
    if weights_map is None:
        weights_map = INTERACTION_WEIGHTS

    df = interactions_df.copy()
    df["weight"] = df["interaction_type"].map(lambda t: weights_map.get(t, 1.0))

    # Sum weights for repeated customer-product pairs
    agg = df.groupby(["customer_id", "product_id"], as_index=False)["weight"].sum()

    unique_users = sorted(agg["customer_id"].unique())
    unique_items = sorted(agg["product_id"].unique())

    user_to_idx = {u: i for i, u in enumerate(unique_users)}
    idx_to_user = {i: u for i, u in enumerate(unique_users)}
    item_to_idx = {p: i for i, p in enumerate(unique_items)}
    idx_to_item = {i: p for i, p in enumerate(unique_items)}

    row_indices = agg["customer_id"].map(user_to_idx).values
    col_indices = agg["product_id"].map(item_to_idx).values
    values = agg["weight"].values

    mat = csr_matrix(
        (values, (row_indices, col_indices)),
        shape=(len(unique_users), len(unique_items)),
        dtype=np.float32,
    )
    logger.info(f"Built interaction matrix: shape {mat.shape}, non-zero elements: {mat.nnz}")
    return mat, user_to_idx, idx_to_user, item_to_idx, idx_to_item
