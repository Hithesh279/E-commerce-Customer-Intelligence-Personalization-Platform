"""
api/schemas/review.py
Pydantic schemas for review analysis requests and NLP outputs.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewAnalysisRequest(BaseModel):
    review_text: str = Field(
        ...,
        min_length=3,
        json_schema_extra={"example": "The battery lasts all day, but the camera is disappointing."}
    )


class ExtractedAspectItem(BaseModel):
    aspect: str
    sentiment: str
    sentiment_score: float
    snippet: Optional[str] = None


class ReviewAnalysisResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    probabilities: Dict[str, float]
    aspects: List[ExtractedAspectItem]
