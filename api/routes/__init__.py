"""
api/routes package.
"""
from api.routes.customers import router as customers_router
from api.routes.products import router as products_router
from api.routes.recommendations import router as recommendations_router
from api.routes.reviews import router as reviews_router

__all__ = [
    "customers_router",
    "products_router",
    "recommendations_router",
    "reviews_router",
]
