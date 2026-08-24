"""LangGraph state definition for the SaaS Support Copilot pipeline.

The state flows through: classify → retrieve → fuse → rerank → confidence → generate → format.
"""

from typing import TypedDict, Optional


class CopilotState(TypedDict):
    """Typed state dict for the LangGraph pipeline."""

    # --- Input ---
    ticket_text: str
    session_id: str
    conversation_history: list[dict]  # [{role: "user"/"assistant", content: str}]

    # --- Routing ---
    routed_sources: list[str]

    # --- Retrieval ---
    semantic_results: list[dict]
    bm25_results: list[dict]
    fused_results: list[dict]
    reranked_results: list[dict]

    # --- Confidence & Escalation ---
    confidence_score: float
    escalated: bool
    escalation_reason: str

    # --- Generation ---
    draft_response: str
    cited_sources: list[dict]

    # --- Error tracking ---
    error: Optional[str]
    retrieval_empty: bool
