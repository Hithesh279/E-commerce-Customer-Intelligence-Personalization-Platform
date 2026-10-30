"""
api/routes/recommendations.py
Personalized recommendation endpoints.
"""
import inspect
from typing import Optional
from fastapi import APIRouter, Depends, Path, Query
from api.dependencies import get_service
from api.schemas.recommendation import RecommendationResponse
from api.services.api_service import APIService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

_PATTERN_KW = "pattern" if "pattern" in inspect.signature(Query).parameters else "regex"


@router.get(
    "/{customer_id}",
    response_model=RecommendationResponse,
    summary="Get Personalized Recommendations",
    description="Generate Top-K personalized product recommendations with explainability rationale.",
)
def get_recommendations_for_customer(
    customer_id: str = Path(..., examples=["CUST_00001"]),
    strategy: Optional[str] = Query("hybrid", **{_PATTERN_KW: "^(hybrid|collaborative|content|popularity)$"}),
    top_k: Optional[int] = Query(10, ge=1, le=20),
    service: APIService = Depends(get_service),
):
    """Return recommendations."""
    return service.get_recommendations(customer_id=customer_id, strategy=strategy, top_k=top_k)
