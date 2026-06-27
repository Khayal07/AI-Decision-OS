"""SSE streaming test with a mocked LLM (no network)."""

import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.fakes import fake_complete_json

TOKEN = {"X-Service-Token": "dev-internal-token"}


@pytest.fixture(autouse=True)
def _mock_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.graph.nodes.complete_json", fake_complete_json)


def test_analyze_streams_status_and_result() -> None:
    client = TestClient(app)
    events: list[tuple[str, str]] = []

    with client.stream(
        "POST", "/analyze", json={"query": "MacBook Air or Pro?"}, headers=TOKEN
    ) as response:
        assert response.status_code == 200
        event = ""
        for line in response.iter_lines():
            if line.startswith("event:"):
                event = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                events.append((event, line.split(":", 1)[1].strip()))

    names = [e for e, _ in events]
    assert "status" in names
    assert "result" in names
    assert "done" in names

    result_payload = next(data for name, data in events if name == "result")
    result = json.loads(result_payload)
    assert result["winner"] == result["options"][0]["name"]
    assert result["options"][0]["is_winner"] is True
