"""
src/recommendation/explainability.py
Generates transparent, human-readable recommendation explanations from actual model signals.
"""
from typing import Dict, Optional


def generate_recommendation_reason(
    product_name: str,
    category: str,
    collab_score: float,
    content_score: float,
    popularity_score: float,
    dominant_source_product: Optional[str] = None,
    is_cold_start: bool = False,
) -> str:
    """
    Generate an explainable rationale for why a product is recommended based on model score signals.
    """
    if is_cold_start:
        return f"Trending top seller in {category} popular among new members"

    if dominant_source_product:
        return f"Because you showed interest in {dominant_source_product}"

    # Determine dominant model signal
    if collab_score >= content_score and collab_score >= popularity_score and collab_score > 0.3:
        return "Customers with similar shopping and browsing behavior frequently chose this"
    elif content_score >= collab_score and content_score >= popularity_score and content_score > 0.3:
        return f"Matches your affinity for {category} features based on your interaction history"
    else:
        return f"Top-rated best-seller in {category} with verified customer satisfaction"
