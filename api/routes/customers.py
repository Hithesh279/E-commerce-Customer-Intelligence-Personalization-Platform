"""
api/routes/customers.py
Customer analytics endpoints.
"""
from fastapi import APIRouter, Depends, Path
from api.dependencies import get_service
from api.schemas.customer import CustomerProfileResponse
from api.services.api_service import APIService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "/{customer_id}",
    response_model=CustomerProfileResponse,
    summary="Get Customer 360 Profile",
    description="Retrieve comprehensive customer profile including RFM segmentation, lifetime spend, and orders.",
)
def get_customer_by_id(
    customer_id: str = Path(..., examples=["CUST_00001"]),
    service: APIService = Depends(get_service),
):
    """Fetch customer profile."""
    return service.get_customer(customer_id)
