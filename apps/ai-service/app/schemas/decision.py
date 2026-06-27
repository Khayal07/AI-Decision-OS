"""Decision request/response contracts.

These are intentionally minimal in Phase 0. The full structured decision schema
(options, criteria, scores, risks, evidence, confidence) is built in Phase 1
alongside the LangGraph multi-agent graph.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str = "ai-service"
    version: str = "0.0.0"


class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's decision in natural language.")
    decision_id: str | None = Field(default=None, description="Existing decision id, if any.")
    user_id: str | None = Field(default=None, description="Owner id, for personalization.")


class AnalyzeAccepted(BaseModel):
    decision_id: str | None
    status: str
    message: str
