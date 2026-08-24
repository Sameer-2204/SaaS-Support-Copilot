"""LangGraph state graph construction.

Builds and compiles the copilot pipeline as a LangGraph StateGraph.
The graph flows:
  START → classify_and_route → [retrieve_semantic, retrieve_bm25]
  → fuse_results → rerank_results → compute_confidence
  → generate_response → format_response → END

Semantic and BM25 retrieval run as sequential nodes (LangGraph handles
the edges). Both feed into fuse_results.
"""

from langgraph.graph import StateGraph, START, END
from app.graph.state import CopilotState
from app.graph.nodes import (
    classify_and_route,
    retrieve_semantic,
    retrieve_bm25,
    fuse_results,
    rerank_results,
    compute_confidence,
    generate_response,
    format_response,
)


def build_graph() -> StateGraph:
    """Construct and compile the copilot LangGraph pipeline.

    Returns:
        A compiled LangGraph that can be invoked with ainvoke().
    """
    graph = StateGraph(CopilotState)

    # Add all nodes
    graph.add_node("classify_and_route", classify_and_route)
    graph.add_node("retrieve_semantic", retrieve_semantic)
    graph.add_node("retrieve_bm25", retrieve_bm25)
    graph.add_node("fuse_results", fuse_results)
    graph.add_node("rerank_results", rerank_results)
    graph.add_node("compute_confidence", compute_confidence)
    graph.add_node("generate_response", generate_response)
    graph.add_node("format_response", format_response)

    # Define edges
    # START → classify
    graph.add_edge(START, "classify_and_route")

    # classify → both retrievals (sequential, not parallel fan-out to keep it simple)
    graph.add_edge("classify_and_route", "retrieve_semantic")
    graph.add_edge("retrieve_semantic", "retrieve_bm25")

    # Both retrievals → fuse
    graph.add_edge("retrieve_bm25", "fuse_results")

    # fuse → rerank → confidence
    graph.add_edge("fuse_results", "rerank_results")
    graph.add_edge("rerank_results", "compute_confidence")

    # confidence → generate (always generates, escalation flag is in state)
    graph.add_edge("compute_confidence", "generate_response")

    # generate → format → END
    graph.add_edge("generate_response", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


# Singleton compiled graph
copilot_graph = build_graph()
