"""
api/schemas package.
"""
from api.schemas.customer import CustomerProfileResponse
from api.schemas.product import ProductProfileResponse, ProductSentimentResponse, SimilarProductItem
from api.schemas.recommendation import RecommendationResponse, RecommendedProduct
from api.schemas.review import ExtractedAspectItem, ReviewAnalysisRequest, ReviewAnalysisResponse

__all__ = [
    "CustomerProfileResponse",
    "ProductProfileResponse",
    "ProductSentimentResponse",
    "SimilarProductItem",
    "RecommendedProduct",
    "RecommendationResponse",
    "ReviewAnalysisRequest",
    "ExtractedAspectItem",
    "ReviewAnalysisResponse",
]
