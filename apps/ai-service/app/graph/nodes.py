"""LangGraph nodes.

Pipeline: analyze → rank → (research ‖ risk ‖ financial ‖ psychology) → judge →
verifier → assemble. The assemble node merges everything deterministically.
"""

from app.config import get_settings
from app.graph.prompts import (
    ANALYZER_SYS,
    FINANCIAL_SYS,
    JUDGE_SYS,
    PSYCHOLOGY_SYS,
    RANKING_SYS,
    RESEARCH_SYS,
    RISK_SYS,
    VERIFIER_SYS,
)
from app.graph.state import GraphState
from app.router.llm import complete_json
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
from app.scoring.aggregate import aggregate, margin_confidence


def _options_line(state: GraphState) -> str:
    analyzer = state["analyzer"]
    return f"Decision: {analyzer.title}\nOptions: {', '.join(analyzer.options)}"


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
        system=RANKING_SYS, user=user, schema=RankingOutput, model=get_settings().model_subagent
    )
    return {"ranking": ranking}


async def research_node(state: GraphState) -> GraphState:
    research = await complete_json(
        system=RESEARCH_SYS,
        user=_options_line(state),
        schema=ResearchOutput,
        model=get_settings().model_subagent,
    )
    return {"research": research}


async def risk_node(state: GraphState) -> GraphState:
    risk = await complete_json(
        system=RISK_SYS,
        user=_options_line(state),
        schema=RiskOutput,
        model=get_settings().model_subagent,
    )
    return {"risk": risk}


async def financial_node(state: GraphState) -> GraphState:
    financial = await complete_json(
        system=FINANCIAL_SYS,
        user=_options_line(state),
        schema=FinancialOutput,
        model=get_settings().model_subagent,
    )
    return {"financial": financial}


async def psychology_node(state: GraphState) -> GraphState:
    psychology = await complete_json(
        system=PSYCHOLOGY_SYS,
        user=_options_line(state),
        schema=PsychologyOutput,
        model=get_settings().model_subagent,
    )
    return {"psychology": psychology}


async def judge_node(state: GraphState) -> GraphState:
    analyzer = state["analyzer"]
    ranking = state["ranking"]
    lines = [
        f"{o.name}: " + ", ".join(f"{s.criterion}={s.score}" for s in o.scores)
        for o in ranking.options
    ]
    user = f"Decision: {analyzer.title}\nScores:\n" + "\n".join(lines)
    judge = await complete_json(
        system=JUDGE_SYS, user=user, schema=JudgeOutput, model=get_settings().model_judge
    )
    return {"judge": judge}


async def verifier_node(state: GraphState) -> GraphState:
    judge = state["judge"]
    user = f"Winner: {judge.winner}\nConfidence: {judge.confidence}\nReasoning: {judge.reasoning}"
    verifier = await complete_json(
        system=VERIFIER_SYS, user=user, schema=VerifierOutput, model=get_settings().model_judge
    )
    return {"verifier": verifier}


async def assemble_node(state: GraphState) -> GraphState:
    """Deterministic assembly: merge specialist outputs, compute confidence in code."""
    analyzer = state["analyzer"]
    options = aggregate(analyzer, state["ranking"])

    risk_by = {o.name: o for o in state["risk"].options}
    fin_by = {o.name: o for o in state["financial"].options}
    psy_by = {o.name: o for o in state["psychology"].options}

    for option in options:
        if risk := risk_by.get(option.name):
            option.risk_level = risk.risk_level
            option.risks = risk.risks
        if fin := fin_by.get(option.name):
            option.upfront_cost = fin.upfront_cost
            option.long_term_value = fin.long_term_value
        if psy := psy_by.get(option.name):
            option.regret_risk = psy.regret_risk
            option.fit = psy.fit

    judge = state["judge"]
    verifier = state["verifier"]
    base = (judge.confidence + margin_confidence(options)) / 2
    confidence = round(max(0.0, min(100.0, base + verifier.confidence_adjustment)), 1)

    result = DecisionResult(
        title=analyzer.title,
        decision_type=analyzer.decision_type,
        criteria=analyzer.criteria,
        options=options,
        winner=options[0].name,  # deterministic ranking decides the winner
        confidence=confidence,
        recommendation=judge.recommendation,
        reasoning=judge.reasoning,
        evidence=state["research"].evidence,
        verifier_issues=verifier.issues,
    )
    return {"result": result}
