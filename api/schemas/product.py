"""
api/schemas/product.py
Pydantic schemas for product information and sentiment summaries.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class SimilarProductItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    price: float
    score: float
    reason: str


class ProductSentimentResponse(BaseModel):
    product_id: str
    product_name: str
    category: str
    review_count: int
    average_rating: float
    positive_sentiment_pct: float
    negative_sentiment_pct: float
    top_aspects: List[Dict[str, Any]]
