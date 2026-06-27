"""API routes for the AI service.

`/analyze` runs the LangGraph pipeline and streams agent progress + the final
decision over Server-Sent Events. The Next.js BFF authenticates with a shared
service token and proxies the stream to the browser.
"""

import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sse_starlette.sse import EventSourceResponse

from app import __version__
from app.config import get_settings
from app.graph.build import build_graph
from app.graph.prompts import CLARIFY_SYS
from app.router.llm import complete_json
from app.schemas.decision import (
    AnalyzeRequest,
    ClarifyResponse,
    HealthResponse,
)

router = APIRouter()

NODE_LABELS = {
    "analyze": "Understanding the decision",
    "rank": "Scoring the options",
    "research": "Gathering evidence",
    "risk": "Assessing risks",
    "financial": "Analyzing costs",
    "psychology": "Checking fit & regret",
    "judge": "Weighing the verdict",
    "verifier": "Verifying consistency",
    "assemble": "Finalizing recommendation",
}


async def require_service_token(x_service_token: Annotated[str, Header()] = "") -> None:
    """Reject calls that don't present the shared service token."""
    if x_service_token != get_settings().ai_service_token:
        raise HTTPException(status_code=401, detail="invalid service token")


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    """Liveness probe."""
    return HealthResponse(status="ok", version=__version__)


async def _decision_events(query: str) -> AsyncIterator[dict[str, str]]:
    graph = build_graph()
    try:
        async for chunk in graph.astream({"query": query}, stream_mode="updates"):
            for node, update in chunk.items():
                yield {
                    "event": "status",
                    "data": json.dumps({"node": node, "label": NODE_LABELS.get(node, node)}),
                }
                if node == "assemble":
                    yield {"event": "result", "data": update["result"].model_dump_json()}
        yield {"event": "done", "data": "{}"}
    except Exception as exc:  # surface failures to the client as an SSE error event
        yield {"event": "error", "data": json.dumps({"message": str(exc)})}


@router.post(
    "/clarify",
    tags=["decisions"],
    dependencies=[Depends(require_service_token)],
)
async def clarify(request: AnalyzeRequest) -> ClarifyResponse:
    """Return up to 3 clarifying questions — or none if the decision is clear."""
    response = await complete_json(
        system=CLARIFY_SYS,
        user=request.query,
        schema=ClarifyResponse,
        model=get_settings().model_subagent,
    )
    response.questions = response.questions[:3]
    return response


@router.post("/analyze", tags=["decisions"], dependencies=[Depends(require_service_token)])
async def analyze(request: AnalyzeRequest) -> EventSourceResponse:
    """Stream the multi-agent decision pipeline as Server-Sent Events."""
    return EventSourceResponse(_decision_events(request.query))
