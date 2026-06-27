"""API routes for the AI service.

Phase 0 exposes a health check and a stubbed `/analyze` endpoint so the BFF
integration contract exists end to end. The multi-agent pipeline (LangGraph)
and SSE streaming land in Phase 1.
"""

from fastapi import APIRouter

from app import __version__
from app.schemas.decision import AnalyzeRequest, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse(status="ok", version=__version__)


@router.post("/analyze", tags=["decisions"])
async def analyze(request: AnalyzeRequest) -> dict[str, str | None]:
    """Run the multi-agent decision pipeline (SSE streaming added in the next step)."""
    return {
        "decision_id": request.decision_id,
        "status": "not_implemented",
        "message": "SSE streaming endpoint lands next.",
    }
