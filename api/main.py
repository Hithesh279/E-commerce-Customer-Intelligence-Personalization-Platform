"""
api/main.py
FastAPI entry point for the E-commerce Customer Intelligence Platform.

Configuration (environment variables):
  CORS_ALLOW_ORIGINS  Comma-separated browser origins allowed to call the API.
                      Default: http://localhost:8501,http://127.0.0.1:8501
  API_KEY             When set, every data endpoint requires the header "X-API-Key: <value>".
                      Health and root endpoints stay open for liveness checks.
"""
import os
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from api.dependencies import get_service
from api.routes.customers import router as customers_router
from api.routes.products import router as products_router
from api.routes.recommendations import router as recommendations_router
from api.routes.reviews import router as reviews_router
from api.services.api_service import APIService

DEFAULT_CORS_ORIGINS = "http://localhost:8501,http://127.0.0.1:8501"

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _cors_origins() -> List[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def require_api_key(provided: Optional[str] = Security(_api_key_header)) -> None:
    """Enforce the API key when API_KEY is configured; otherwise allow all requests."""
    expected = os.getenv("API_KEY")
    if expected and provided != expected:
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header.")


app = FastAPI(
    title="E-commerce Customer Intelligence & Personalization API",
    description=(
        "REST API for executive analytics, customer 360 intelligence, personalized recommendations, "
        "review sentiment classification, and aspect-level sentiment extraction."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

protected = [Depends(require_api_key)]
app.include_router(customers_router, dependencies=protected)
app.include_router(products_router, dependencies=protected)
app.include_router(recommendations_router, dependencies=protected)
app.include_router(reviews_router, dependencies=protected)


@app.get("/analytics/kpis", tags=["Analytics"], dependencies=protected, summary="Get Executive Business KPIs")
def get_executive_kpis(service: APIService = Depends(get_service)) -> Dict[str, Any]:
    """Return high-level executive commercial and customer satisfaction KPIs."""
    return service.get_executive_kpis()


@app.get("/analytics/powerbi/export", tags=["Analytics"], dependencies=protected, summary="Download Power BI Star-Schema Package")
def download_powerbi_export(format: str = "zip"):
    """
    Download Power BI Star-Schema files directly.
    - format='zip' (default): Full package containing all 7 Fact/Dim tables, Excel model, 16 DAX measures & PBIP.
    - format='xlsx': Consolidated Power BI Star-Schema Excel workbook.
    """
    from fastapi.responses import FileResponse
    from src.database.db_manager import build_powerbi_package_zip
    from src.utils.config import POWERBI_DATA_DIR

    if format == "xlsx":
        xlsx_path = POWERBI_DATA_DIR / "Ecommerce_Star_Schema.xlsx"
        if not xlsx_path.exists():
            from src.database.db_manager import DatabaseManager
            DatabaseManager().export_powerbi_star_schema()
        return FileResponse(
            path=str(xlsx_path),
            filename="Ecommerce_Star_Schema.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        zip_path = POWERBI_DATA_DIR / "Ecommerce_PowerBI_Package.zip"
        if not zip_path.exists():
            build_powerbi_package_zip(zip_path)
        return FileResponse(
            path=str(zip_path),
            filename="Ecommerce_PowerBI_Package.zip",
            media_type="application/zip",
        )


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
