"""Shared test doubles."""

from typing import Any

from app.schemas.decision import (
    AnalyzerOutput,
    ClarifyQuestion,
    ClarifyResponse,
    Criterion,
    CriterionScore,
    EvidenceItem,
    FinancialOutput,
    JudgeOutput,
    OptionFinance,
    OptionPsychology,
    OptionRisk,
    PsychologyOutput,
    RankedOption,
    RankingOutput,
    ResearchOutput,
    RiskItem,
    RiskOutput,
    VerifierOutput,
)

_OPTIONS = ["MacBook Air", "MacBook Pro"]


async def fake_complete_json(*, schema: type[Any], **_: Any) -> Any:
    """Return canned, schema-valid agent outputs without calling any model."""
    if schema is AnalyzerOutput:
        return AnalyzerOutput(
            title="MacBook Air vs Pro",
            decision_type="purchase",
            options=_OPTIONS,
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
    if schema is ResearchOutput:
        return ResearchOutput(
            evidence=[EvidenceItem(claim="Air is lighter", credibility=0.9, supports="MacBook Air")]
        )
    if schema is RiskOutput:
        return RiskOutput(
            options=[
                OptionRisk(
                    name=name,
                    risk_level="low",
                    risks=[RiskItem(description="May feel underpowered", severity=2, likelihood=2)],
                )
                for name in _OPTIONS
            ]
        )
    if schema is FinancialOutput:
        return FinancialOutput(
            options=[
                OptionFinance(name="MacBook Air", upfront_cost=999, long_term_value=8),
                OptionFinance(name="MacBook Pro", upfront_cost=1599, long_term_value=9),
            ]
        )
    if schema is PsychologyOutput:
        return PsychologyOutput(
            options=[
                OptionPsychology(name="MacBook Air", regret_risk=3, fit=8),
                OptionPsychology(name="MacBook Pro", regret_risk=4, fit=7),
            ]
        )
    if schema is ClarifyResponse:
        # four questions, to verify the route truncates to three
        return ClarifyResponse(
            questions=[ClarifyQuestion(question=f"Q{i}?", options=["a", "b"]) for i in range(4)]
        )
    if schema is VerifierOutput:
        return VerifierOutput(consistent=True, issues=[], confidence_adjustment=5)
    return JudgeOutput(
        winner="MacBook Air",
        confidence=70,
        recommendation="Pick the Air.",
        reasoning="Best balance for your priorities.",
    )
