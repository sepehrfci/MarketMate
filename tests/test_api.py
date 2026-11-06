from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_status_endpoint():
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json()["app"] == "MarketMate"
    assert response.json()["status"] == "running"


def test_metrics_endpoint():
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "marketmate_http_requests_total" in response.text
