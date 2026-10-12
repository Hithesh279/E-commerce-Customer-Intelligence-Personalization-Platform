"""
api/schemas/recommendation.py
Pydantic schemas for recommendation requests and responses.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendedProduct(BaseModel):
    product_id: str
    product_name: str
    category: str
    price: float
    score: float
    reason: str


class RecommendationResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    customer_id: str
    model_strategy: str
    count: int
    recommendations: List[RecommendedProduct]
