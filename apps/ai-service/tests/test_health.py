"""Smoke + auth/validation tests for the API."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TOKEN = {"X-Service-Token": "dev-internal-token"}


def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "ai-service"


def test_analyze_requires_token() -> None:
    response = client.post("/analyze", json={"query": "A or B?"})
    assert response.status_code == 401


def test_analyze_rejects_empty_query() -> None:
    response = client.post("/analyze", json={"query": ""}, headers=TOKEN)
    assert response.status_code == 422
