"""Shared state for the LangGraph decision pipeline."""

from typing import TypedDict

from app.schemas.decision import AnalyzerOutput, DecisionResult, JudgeOutput, RankingOutput


class GraphState(TypedDict, total=False):
    query: str
    analyzer: AnalyzerOutput
    ranking: RankingOutput
    judge: JudgeOutput
    result: DecisionResult
