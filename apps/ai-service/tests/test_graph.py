"""Graph pipeline test with a mocked LLM (no network)."""

from typing import Any

import pytest

from app.graph.build import build_graph
from app.schemas.decision import (
    AnalyzerOutput,
    Criterion,
    CriterionScore,
    DecisionResult,
    JudgeOutput,
    RankedOption,
    RankingOutput,
)


async def _fake_complete_json(*, schema: type[Any], **_: Any) -> Any:
    if schema is AnalyzerOutput:
        return AnalyzerOutput(
            title="MacBook Air vs Pro",
            decision_type="purchase",
            options=["MacBook Air", "MacBook Pro"],
            criteria=[
                Criterion(name="portability", weight=0.5),
                Criterion(name="performance", weight=0.5),
            ],
        )
    if schema is RankingOutput:
        return RankingOutput(
            options=[
                RankedOption(
                    name="MacBook Air",
                    scores=[
                        CriterionScore(criterion="portability", score=9),
                        CriterionScore(criterion="performance", score=6),
                    ],
                    pros=["Light"],
                    cons=["Less power"],
                ),
                RankedOption(
                    name="MacBook Pro",
                    scores=[
                        CriterionScore(criterion="portability", score=5),
                        CriterionScore(criterion="performance", score=9),
                    ],
                    pros=["Fast"],
                    cons=["Heavy"],
                ),
            ]
        )
    return JudgeOutput(
        winner="MacBook Air",
        confidence=70,
        recommendation="Pick the Air.",
        reasoning="Best balance for your priorities.",
    )


@pytest.mark.asyncio
async def test_graph_runs_end_to_end(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.graph.nodes.complete_json", _fake_complete_json)
    graph = build_graph()

    final = await graph.ainvoke({"query": "MacBook Air or Pro?"})
    result = final["result"]

    assert isinstance(result, DecisionResult)
    assert len(result.options) == 2
    assert result.options[0].rank == 1
    assert result.options[0].is_winner is True
    assert result.winner == result.options[0].name
    assert 0 <= result.confidence <= 100
