# AI Service

The multi-agent decision reasoning engine for AI Decision OS (FastAPI + LangGraph).

## Local development

```bash
cd apps/ai-service
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

- Health check: `GET http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

## Testing & linting

```bash
pytest          # tests
ruff check .    # lint
mypy app        # type-check
```

## Structure

```
app/
  api/        # HTTP routes (health, analyze)
  graph/      # LangGraph multi-agent nodes (Phase 1+)
  router/     # provider-agnostic model router
  scoring/    # deterministic scoring math (TCO, weights, sensitivity)
  tools/      # web search, retrieval, calculator
  schemas/    # Pydantic contracts
  evals/      # golden-set eval harness
```

> Targets Python 3.12 (CI pin). The multi-agent pipeline and SSE streaming land in Phase 1.
