"""Smoke tests for the Phase 0 skeleton."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "ai-service"


def test_analyze_stub_accepts_query() -> None:
    response = client.post("/analyze", json={"query": "MacBook Air or Pro?"})
    assert response.status_code == 200
    assert response.json()["status"] == "not_implemented"


def test_analyze_rejects_empty_query() -> None:
    response = client.post("/analyze", json={"query": ""})
    assert response.status_code == 422
