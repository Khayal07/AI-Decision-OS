"""Decision request/response contracts.

Three layers:
- request/response envelopes (`AnalyzeRequest`, `HealthResponse`)
- per-agent structured outputs (`AnalyzerOutput`, `RankingOutput`, `JudgeOutput`)
- the assembled `DecisionResult` the dashboard renders
"""

from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["higher_better", "lower_better"]


# --- envelopes ---------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    service: str = "ai-service"
    version: str = "0.0.0"


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's decision in natural language.")
    decision_id: str | None = Field(default=None, description="Existing decision id, if any.")
    user_id: str | None = Field(default=None, description="Owner id, for personalization.")


# --- shared ------------------------------------------------------------------
class Criterion(BaseModel):
    name: str
    weight: float = Field(..., ge=0, le=1, description="Relative importance, 0..1.")
    direction: Direction = "higher_better"


# --- agent outputs -----------------------------------------------------------
class AnalyzerOutput(BaseModel):
    """Decision Analyzer: structure the problem."""

    title: str
    decision_type: str
    options: list[str] = Field(..., min_length=2)
    criteria: list[Criterion] = Field(..., min_length=2)


class CriterionScore(BaseModel):
    criterion: str
    score: float = Field(..., ge=0, le=10, description="Raw score for this criterion, 0..10.")


class RankedOption(BaseModel):
    name: str
    scores: list[CriterionScore]
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


class RankingOutput(BaseModel):
    """Ranking Agent: score every option on every criterion."""

    options: list[RankedOption] = Field(..., min_length=2)


class JudgeOutput(BaseModel):
    """Final Judge: pick a winner and explain it."""

    winner: str
    confidence: float = Field(..., ge=0, le=100)
    recommendation: str
    reasoning: str


# --- assembled result --------------------------------------------------------
class OptionResult(BaseModel):
    name: str
    overall_score: float = Field(..., ge=0, le=100)
    rank: int
    is_winner: bool = False
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    criterion_scores: dict[str, float] = Field(default_factory=dict)


class DecisionResult(BaseModel):
    title: str
    decision_type: str
    criteria: list[Criterion]
    options: list[OptionResult]
    winner: str
    confidence: float = Field(..., ge=0, le=100)
    recommendation: str
    reasoning: str
