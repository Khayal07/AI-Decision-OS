"""Shared test doubles."""

from typing import Any

from app.schemas.decision import (
    AnalyzerOutput,
    Criterion,
    CriterionScore,
    JudgeOutput,
    RankedOption,
    RankingOutput,
)


async def fake_complete_json(*, schema: type[Any], **_: Any) -> Any:
    """Return canned, schema-valid agent outputs without calling any model."""
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
