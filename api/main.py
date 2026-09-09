"""
api/main.py
FastAPI entry point for the E-commerce Customer Intelligence Platform.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.customers import router as customers_router
from api.routes.products import router as products_router
from api.routes.recommendations import router as recommendations_router
from api.routes.reviews import router as reviews_router

app = FastAPI(
    title="E-commerce Customer Intelligence & Personalization API",
    description=(
        "Production-grade REST API providing real-time customer analytics, "
        "personalized multi-strategy recommendations, review NLP sentiment classification, "
        "and 11-aspect sentiment extraction."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(customers_router)
app.include_router(products_router)
app.include_router(recommendations_router)
app.include_router(reviews_router)


@app.get("/", tags=["Health"])
def root():
    """Root status endpoint."""
    return {
        "status": "online",
        "service": "E-commerce Customer Intelligence & Personalization Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for liveness probes."""
    return {"status": "healthy"}
