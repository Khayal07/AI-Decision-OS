"""Tests for the /clarify endpoint with a mocked LLM (no network)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.fakes import fake_complete_json

TOKEN = {"X-Service-Token": "dev-internal-token"}


@pytest.fixture(autouse=True)
def _mock_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.api.routes.complete_json", fake_complete_json)


def test_clarify_requires_token() -> None:
    client = TestClient(app)
    assert client.post("/clarify", json={"query": "A or B?"}).status_code == 401


def test_clarify_returns_at_most_three_questions() -> None:
    client = TestClient(app)
    response = client.post("/clarify", json={"query": "A or B?"}, headers=TOKEN)
    assert response.status_code == 200
    questions = response.json()["questions"]
    assert len(questions) == 3
    assert questions[0]["options"]
