"""Decision request/response contracts.

Layers:
- envelopes (`AnalyzeRequest`, `HealthResponse`)
- per-agent outputs (analyzer, ranking, research, risk, financial, psychology,
  judge, verifier)
- the assembled `DecisionResult` the dashboard renders
"""

from typing import Literal

from pydantic import BaseModel, Field

Direction = Literal["higher_better", "lower_better"]
RiskLevel = Literal["low", "medium", "high"]


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


class RiskItem(BaseModel):
    description: str
    severity: int = Field(..., ge=1, le=5)
    likelihood: int = Field(..., ge=1, le=5)
    mitigation: str | None = None


class EvidenceItem(BaseModel):
    claim: str
    credibility: float = Field(..., ge=0, le=1)
    supports: str | None = Field(default=None, description="Option name this supports, if any.")


# --- agent outputs -----------------------------------------------------------
class AnalyzerOutput(BaseModel):
    title: str
    decision_type: str
    options: list[str] = Field(..., min_length=2)
    criteria: list[Criterion] = Field(..., min_length=2)


class CriterionScore(BaseModel):
    criterion: str
    score: float = Field(..., ge=0, le=10)


class RankedOption(BaseModel):
    name: str
    scores: list[CriterionScore]
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


class RankingOutput(BaseModel):
    options: list[RankedOption] = Field(..., min_length=2)


class ResearchOutput(BaseModel):
    evidence: list[EvidenceItem] = Field(default_factory=list)


class OptionRisk(BaseModel):
    name: str
    risk_level: RiskLevel = "medium"
    risks: list[RiskItem] = Field(default_factory=list)


class RiskOutput(BaseModel):
    options: list[OptionRisk] = Field(..., min_length=1)


class OptionFinance(BaseModel):
    name: str
    upfront_cost: float | None = None
    long_term_value: float = Field(..., ge=0, le=10)
    note: str | None = None


class FinancialOutput(BaseModel):
    options: list[OptionFinance] = Field(..., min_length=1)


class OptionPsychology(BaseModel):
    name: str
    regret_risk: float = Field(..., ge=0, le=10)
    fit: float = Field(..., ge=0, le=10)
    note: str | None = None


class PsychologyOutput(BaseModel):
    options: list[OptionPsychology] = Field(..., min_length=1)


class JudgeOutput(BaseModel):
    winner: str
    confidence: float = Field(..., ge=0, le=100)
    recommendation: str
    reasoning: str


class VerifierOutput(BaseModel):
    consistent: bool = True
    issues: list[str] = Field(default_factory=list)
    confidence_adjustment: float = Field(default=0, ge=-25, le=15)


# --- assembled result --------------------------------------------------------
class OptionResult(BaseModel):
    name: str
    overall_score: float = Field(..., ge=0, le=100)
    rank: int
    is_winner: bool = False
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    criterion_scores: dict[str, float] = Field(default_factory=dict)
    # enriched by the specialist agents (optional)
    risk_level: RiskLevel | None = None
    risks: list[RiskItem] = Field(default_factory=list)
    upfront_cost: float | None = None
    long_term_value: float | None = None
    regret_risk: float | None = None
    fit: float | None = None


class DecisionResult(BaseModel):
    title: str
    decision_type: str
    criteria: list[Criterion]
    options: list[OptionResult]
    winner: str
    confidence: float = Field(..., ge=0, le=100)
    recommendation: str
    reasoning: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    verifier_issues: list[str] = Field(default_factory=list)
