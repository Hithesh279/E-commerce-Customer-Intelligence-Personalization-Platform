"""
tests/test_api.py
Tests for FastAPI endpoints using TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"


def test_get_executive_kpis():
    res = client.get("/analytics/kpis")
    assert res.status_code == 200
    data = res.json()
    assert data["total_net_revenue"] > 0
    assert data["total_orders"] == 1000
    assert data["total_customers"] == 200


def test_get_customer_valid():
    res = client.get("/customers/CUST_00001")
    assert res.status_code == 200
    data = res.json()
    assert data["customer_id"] == "CUST_00001"
    assert "net_spend" in data
    assert "rfm_segment" in data


def test_get_customer_not_found():
    res = client.get("/customers/CUST_NONEXISTENT")
    assert res.status_code == 404


def test_get_product_profile_valid():
    res = client.get("/products/PROD_0001")
    assert res.status_code == 200
    data = res.json()
    assert data["product_id"] == "PROD_0001"
    assert "net_revenue" in data
    assert "units_sold" in data
    assert "is_high_sales_low_sentiment" in data


def test_get_product_profile_not_found():
    res = client.get("/products/PROD_NONEXISTENT")
    assert res.status_code == 404


def test_get_product_sentiment():
    res = client.get("/products/PROD_0005/sentiment")
    assert res.status_code == 200
    data = res.json()
    assert data["product_id"] == "PROD_0005"
    assert "average_rating" in data
    assert "top_aspects" in data


def test_get_recommendations_hybrid():
    res = client.get("/recommendations/CUST_00001?strategy=hybrid&top_k=5")
    assert res.status_code == 200
    data = res.json()
    assert data["customer_id"] == "CUST_00001"
    assert len(data["recommendations"]) == 5
    assert "reason" in data["recommendations"][0]


def test_get_similar_products():
    res = client.get("/products/PROD_0001/similar?top_k=3")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 3


def test_post_review_analysis():
    payload = {"review_text": "The battery lasts all day, but the camera is disappointing."}
    res = client.post("/reviews/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "sentiment" in data
    assert "confidence" in data
    assert len(data["aspects"]) >= 1


def test_get_powerbi_export_zip():
    res = client.get("/analytics/powerbi/export?format=zip")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    assert len(res.content) > 10000


def test_get_powerbi_export_xlsx():
    res = client.get("/analytics/powerbi/export?format=xlsx")
    assert res.status_code == 200
    assert "openxmlformats" in res.headers["content-type"]
    assert len(res.content) > 10000

