"""
api/routes/reviews.py
Review NLP sentiment and aspect extraction endpoints.
"""
from fastapi import APIRouter, Depends
from api.dependencies import get_service
from api.schemas.review import ReviewAnalysisRequest, ReviewAnalysisResponse
from api.services.api_service import APIService

router = APIRouter(prefix="/reviews", tags=["Reviews & NLP"])


@router.post(
    "/analyze",
    response_model=ReviewAnalysisResponse,
    summary="Analyze Review Sentiment & Aspects",
    description="Classify review sentiment, return class probabilities, and extract fine-grained product aspects.",
)
def analyze_review(
    payload: ReviewAnalysisRequest,
    service: APIService = Depends(get_service),
):
    """Analyze customer review."""
    return service.analyze_review(payload.review_text)
