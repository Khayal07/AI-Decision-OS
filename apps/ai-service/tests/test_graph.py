"""Graph pipeline test with a mocked LLM (no network)."""

import pytest

from app.graph.build import build_graph
from app.schemas.decision import DecisionResult
from tests.fakes import fake_complete_json


@pytest.mark.asyncio
async def test_graph_runs_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.graph.nodes.complete_json", fake_complete_json)
    graph = build_graph()

    final = await graph.ainvoke({"query": "MacBook Air or Pro?"})
    result = final["result"]

    assert isinstance(result, DecisionResult)
    assert len(result.options) == 2
    assert result.options[0].rank == 1
    assert result.options[0].is_winner is True
    assert result.winner == result.options[0].name
    assert 0 <= result.confidence <= 100
    # specialist enrichment merged in
    assert result.options[0].risk_level is not None
    assert result.options[0].long_term_value is not None
    assert result.options[0].fit is not None
    assert len(result.evidence) >= 1
