"""
api/schemas/customer.py
Pydantic response models for customer data.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CustomerProfileResponse(BaseModel):
    customer_id: str
    gender: str
    age: Optional[int]
    city: str
    country: str
    membership_type: str
    signup_date: str
    customer_segment: str
    preferred_category: str
    total_orders: int
    net_spend: float
    average_order_value: float
    return_rate: float
    rfm_score: str
    rfm_segment: str
