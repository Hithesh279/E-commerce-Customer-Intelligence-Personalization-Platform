"""
api/dependencies.py
FastAPI dependency injection utilities.
"""
from fastapi import Depends
from api.services.api_service import APIService, get_api_service


def get_service(service: APIService = Depends(get_api_service)) -> APIService:
    """Provide APIService instance to route handlers."""
    return service
