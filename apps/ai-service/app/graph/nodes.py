"""LangGraph nodes for the minimal Analyzer → Ranking → Judge → Assemble pipeline."""

from app.config import get_settings
from app.graph.prompts import ANALYZER_SYS, JUDGE_SYS, RANKING_SYS
from app.graph.state import GraphState
from app.router.llm import complete_json
from app.schemas.decision import (
    AnalyzerOutput,
    DecisionResult,
    JudgeOutput,
    RankingOutput,
)
from app.scoring.aggregate import aggregate, margin_confidence


async def analyze_node(state: GraphState) -> GraphState:
    analyzer = await complete_json(
        system=ANALYZER_SYS,
        user=state["query"],
        schema=AnalyzerOutput,
        model=get_settings().model_subagent,
    )
    return {"analyzer": analyzer}


async def rank_node(state: GraphState) -> GraphState:
    analyzer = state["analyzer"]
    user = (
        f"Decision: {analyzer.title}\n"
        f"Options: {', '.join(analyzer.options)}\n"
        f"Criteria: {', '.join(c.name for c in analyzer.criteria)}"
    )
    ranking = await complete_json(
        system=RANKING_SYS,
        user=user,
        schema=RankingOutput,
        model=get_settings().model_subagent,
    )
    return {"ranking": ranking}


async def judge_node(state: GraphState) -> GraphState:
    analyzer = state["analyzer"]
    ranking = state["ranking"]
    lines = [
        f"{o.name}: " + ", ".join(f"{s.criterion}={s.score}" for s in o.scores)
        for o in ranking.options
    ]
    user = f"Decision: {analyzer.title}\nScores:\n" + "\n".join(lines)
    judge = await complete_json(
        system=JUDGE_SYS,
        user=user,
        schema=JudgeOutput,
        model=get_settings().model_judge,
    )
    return {"judge": judge}


async def assemble_node(state: GraphState) -> GraphState:
    """Deterministic assembly: winner, ranks, and calibrated confidence in code."""
    analyzer = state["analyzer"]
    ranking = state["ranking"]
    judge = state["judge"]

    options = aggregate(analyzer, ranking)
    confidence = round((judge.confidence + margin_confidence(options)) / 2, 1)

    result = DecisionResult(
        title=analyzer.title,
        decision_type=analyzer.decision_type,
        criteria=analyzer.criteria,
        options=options,
        winner=options[0].name,  # deterministic ranking decides the winner
        confidence=confidence,
        recommendation=judge.recommendation,
        reasoning=judge.reasoning,
    )
    return {"result": result}
