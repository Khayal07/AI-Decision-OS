"""Compile the decision graph with a parallel specialist fan-out."""

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes import (
    analyze_node,
    assemble_node,
    financial_node,
    judge_node,
    psychology_node,
    rank_node,
    research_node,
    risk_node,
    verifier_node,
)
from app.graph.state import GraphState

_SPECIALISTS = ("research", "risk", "financial", "psychology")


def build_graph() -> CompiledStateGraph:
    """analyze → rank → (4 specialists in parallel) → judge → verifier → assemble."""
    graph = StateGraph(GraphState)
    graph.add_node("analyze", analyze_node)
    graph.add_node("rank", rank_node)
    graph.add_node("research", research_node)
    graph.add_node("risk", risk_node)
    graph.add_node("financial", financial_node)
    graph.add_node("psychology", psychology_node)
    graph.add_node("judge", judge_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("assemble", assemble_node)

    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "rank")

    # fan out to specialists, then fan in to the judge
    for specialist in _SPECIALISTS:
        graph.add_edge("rank", specialist)
        graph.add_edge(specialist, "judge")

    graph.add_edge("judge", "verifier")
    graph.add_edge("verifier", "assemble")
    graph.add_edge("assemble", END)

    return graph.compile()
