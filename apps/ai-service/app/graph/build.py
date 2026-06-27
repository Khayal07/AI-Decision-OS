"""Compile the decision graph."""

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes import analyze_node, assemble_node, judge_node, rank_node
from app.graph.state import GraphState


def build_graph() -> CompiledStateGraph:
    """Build and compile the Analyzer → Ranking → Judge → Assemble pipeline."""
    graph = StateGraph(GraphState)
    graph.add_node("analyze", analyze_node)
    graph.add_node("rank", rank_node)
    graph.add_node("judge", judge_node)
    graph.add_node("assemble", assemble_node)

    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "rank")
    graph.add_edge("rank", "judge")
    graph.add_edge("judge", "assemble")
    graph.add_edge("assemble", END)

    return graph.compile()
