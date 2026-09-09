"""
api/routes/products.py
Product catalog and sentiment intelligence endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query
from api.dependencies import get_service
from api.schemas.product import ProductSentimentResponse, SimilarProductItem
from api.services.api_service import APIService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/{product_id}/similar",
    response_model=List[SimilarProductItem],
    summary="Get Similar Products",
    description="Retrieve catalog products semantically similar to product_id using TF-IDF cosine similarity.",
)
def get_similar_products(
    product_id: str = Path(..., examples=["PROD_0001"]),
    top_k: Optional[int] = Query(5, ge=1, le=20),
    service: APIService = Depends(get_service),
):
    """Return similar products."""
    return service.get_similar_products(product_id=product_id, top_k=top_k)


@router.get(
    "/{product_id}/sentiment",
    response_model=ProductSentimentResponse,
    summary="Get Product Sentiment Analysis",
    description="Retrieve product sentiment distribution, review count, and fine-grained aspect sentiments.",
)
def get_product_sentiment(
    product_id: str = Path(..., examples=["PROD_0005"]),
    service: APIService = Depends(get_service),
):
    """Return product sentiment analysis."""
    return service.get_product_sentiment(product_id=product_id)
