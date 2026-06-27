"""Deterministic scoring tests (no network)."""

from app.schemas.decision import (
    AnalyzerOutput,
    Criterion,
    CriterionScore,
    RankedOption,
    RankingOutput,
)
from app.scoring.aggregate import aggregate, margin_confidence


def _analyzer() -> AnalyzerOutput:
    return AnalyzerOutput(
        title="A vs B",
        decision_type="purchase",
        options=["A", "B"],
        criteria=[
            Criterion(name="price", weight=0.5),
            Criterion(name="power", weight=0.5),
        ],
    )


def _ranking() -> RankingOutput:
    return RankingOutput(
        options=[
            RankedOption(
                name="A",
                scores=[
                    CriterionScore(criterion="price", score=8),
                    CriterionScore(criterion="power", score=6),
                ],
            ),
            RankedOption(
                name="B",
                scores=[
                    CriterionScore(criterion="price", score=4),
                    CriterionScore(criterion="power", score=4),
                ],
            ),
        ]
    )


def test_aggregate_ranks_and_winner() -> None:
    results = aggregate(_analyzer(), _ranking())
    assert results[0].name == "A"
    assert results[0].rank == 1
    assert results[0].is_winner is True
    assert results[1].is_winner is False
    # A = 0.5*8 + 0.5*6 = 7.0 → 70.0
    assert results[0].overall_score == 70.0


def test_margin_confidence_within_bounds() -> None:
    results = aggregate(_analyzer(), _ranking())
    conf = margin_confidence(results)
    assert 35.0 <= conf <= 95.0
