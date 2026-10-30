"""
api/schemas/product.py
Pydantic schemas for product information, 360 performance profiles, and sentiment summaries.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ProductProfileResponse(BaseModel):
    product_id: str
    product_name: str
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    price: float
    total_orders: int
    units_sold: int
    returned_units: int
    gross_revenue: float
    net_revenue: float
    return_rate: float
    review_count: int
    average_rating: float
    positive_sentiment_pct: float
    negative_sentiment_pct: float
    is_high_sales_low_sentiment: bool
    is_low_sales_high_sentiment: bool


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
