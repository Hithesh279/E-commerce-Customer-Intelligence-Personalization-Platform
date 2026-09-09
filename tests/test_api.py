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
