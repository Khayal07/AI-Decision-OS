"""Shared state for the LangGraph decision pipeline."""

from typing import TypedDict

from app.schemas.decision import (
    AnalyzerOutput,
    DecisionResult,
    FinancialOutput,
    JudgeOutput,
    PsychologyOutput,
    RankingOutput,
    ResearchOutput,
    RiskOutput,
    VerifierOutput,
)


class GraphState(TypedDict, total=False):
    query: str
    analyzer: AnalyzerOutput
    ranking: RankingOutput
    research: ResearchOutput
    risk: RiskOutput
    financial: FinancialOutput
    psychology: PsychologyOutput
    judge: JudgeOutput
    verifier: VerifierOutput
    result: DecisionResult
