"""API routes for the AI service.

Phase 0 exposes a health check and a stubbed `/analyze` endpoint so the BFF
integration contract exists end to end. The multi-agent pipeline (LangGraph)
and SSE streaming land in Phase 1.
"""

from app import __version__
from app.schemas.decision import AnalyzeAccepted, AnalyzeRequest, HealthResponse
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse(status="ok", version=__version__)


@router.post("/analyze", response_model=AnalyzeAccepted, tags=["decisions"])
async def analyze(request: AnalyzeRequest) -> AnalyzeAccepted:
    """Run the multi-agent decision pipeline (stubbed in Phase 0)."""
    return AnalyzeAccepted(
        decision_id=request.decision_id,
        status="not_implemented",
        message="Multi-agent pipeline lands in Phase 1.",
    )
