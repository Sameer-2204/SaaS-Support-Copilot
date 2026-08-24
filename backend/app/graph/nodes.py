"""LangGraph node functions for the SaaS Support Copilot pipeline.

Each node is an async function that takes the current state and returns
a partial state update dict.

Conversation history is managed via an in-memory session store (sufficient
for a portfolio project; production would use Redis or a database).
"""

import json
import os
from collections import defaultdict
from app.graph.state import CopilotState
from app.retrieval.router import route_query, should_escalate, get_contact_for_query
from app.retrieval.semantic import semantic_search
from app.retrieval.keyword import bm25_search
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import Reranker
from app.llm.groq_client import generate_completion
from app.config import settings


# --- Contact information ---
_CONTACTS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "contacts.json")
try:
    with open(_CONTACTS_PATH, encoding="utf-8") as _f:
        CONTACTS = json.load(_f)
except (FileNotFoundError, json.JSONDecodeError):
    CONTACTS = {}


# --- In-memory session store ---
_session_store: dict[str, list[dict]] = defaultdict(list)

# Lazy-loaded reranker singleton
_reranker: Reranker | None = None


def _get_reranker() -> Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker


def get_history(session_id: str) -> list[dict]:
    """Get conversation history for a session."""
    return _session_store.get(session_id, [])


def save_turn(session_id: str, user_msg: str, assistant_msg: str):
    """Save a conversation turn to the session store."""
    _session_store[session_id].append({"role": "user", "content": user_msg})
    _session_store[session_id].append({"role": "assistant", "content": assistant_msg})


# =========================================================================
# Node 1: Classify and Route
# =========================================================================
async def classify_and_route(state: CopilotState) -> dict:
    """Analyze ticket text to determine which source types to query."""
    try:
        sources = route_query(state["ticket_text"])
        return {"routed_sources": sources}
    except Exception as e:
        return {
            "routed_sources": ["product_docs", "resolved_ticket", "changelog", "api_error"],
            "error": f"Routing failed, using all sources: {str(e)}",
        }


# =========================================================================
# Node 2: Semantic Retrieval
# =========================================================================
async def retrieve_semantic(state: CopilotState) -> dict:
    """Embed query and search pgvector for semantically similar chunks."""
    try:
        results = await semantic_search(
            state["ticket_text"],
            state["routed_sources"],
            top_k=settings.MAX_RETRIEVAL_RESULTS,
        )
        return {
            "semantic_results": results,
            "retrieval_empty": len(results) == 0,
        }
    except Exception as e:
        return {
            "semantic_results": [],
            "retrieval_empty": True,
            "error": f"Semantic search failed: {str(e)}",
        }


# =========================================================================
# Node 3: BM25 Retrieval
# =========================================================================
async def retrieve_bm25(state: CopilotState) -> dict:
    """Search the BM25 index for keyword-relevant chunks.

    Note: bm25, chunk_ids, and chunks_lookup are injected via app.state
    at runtime. This node accesses them through a module-level reference
    set during app startup.
    """
    try:
        from app.graph.nodes import _bm25_state  # Set during app startup

        results = bm25_search(
            state["ticket_text"],
            _bm25_state["bm25"],
            _bm25_state["chunk_ids"],
            _bm25_state["chunks_lookup"],
            state["routed_sources"],
            top_k=settings.MAX_RETRIEVAL_RESULTS,
        )
        return {"bm25_results": results}
    except Exception as e:
        return {
            "bm25_results": [],
            "error": f"BM25 search failed: {str(e)}",
        }


# Module-level reference for BM25 state (set during app startup)
_bm25_state: dict = {}


def set_bm25_state(bm25, chunk_ids, chunks_lookup):
    """Called during app startup to inject BM25 dependencies."""
    global _bm25_state
    _bm25_state = {
        "bm25": bm25,
        "chunk_ids": chunk_ids,
        "chunks_lookup": chunks_lookup,
    }


# =========================================================================
# Node 4: Fuse Results
# =========================================================================
async def fuse_results(state: CopilotState) -> dict:
    """Merge semantic and BM25 results using Reciprocal Rank Fusion."""
    fused = reciprocal_rank_fusion(
        state.get("semantic_results", []),
        state.get("bm25_results", []),
    )
    return {
        "fused_results": fused,
        "retrieval_empty": len(fused) == 0,
    }


# =========================================================================
# Node 5: Rerank Results
# =========================================================================
async def rerank_results(state: CopilotState) -> dict:
    """Rerank fused candidates with the cross-encoder."""
    if not state.get("fused_results"):
        return {"reranked_results": [], "retrieval_empty": True}

    reranker = _get_reranker()
    reranked = await reranker.arerank(
        state["ticket_text"],
        state["fused_results"],
        top_k=settings.TOP_K_FINAL,
    )
    return {"reranked_results": reranked}


# =========================================================================
# Node 6: Compute Confidence
# =========================================================================
async def compute_confidence(state: CopilotState) -> dict:
    """Calculate confidence score and determine escalation."""
    reranker = _get_reranker()
    confidence = reranker.compute_confidence(state.get("reranked_results", []))
    escalated = should_escalate(confidence, settings.CONFIDENCE_THRESHOLD)

    escalation_reason = ""
    if escalated:
        escalation_reason = (
            f"Confidence score {confidence:.2f} is below threshold "
            f"{settings.CONFIDENCE_THRESHOLD}. Escalated for human review."
        )

    return {
        "confidence_score": confidence,
        "escalated": escalated,
        "escalation_reason": escalation_reason,
    }


# =========================================================================
# Node 7: Generate Response
# =========================================================================
async def generate_response(state: CopilotState) -> dict:
    """Generate a cited draft response using the Groq LLM."""
    prompt = _build_prompt(state)
    response_text = await generate_completion(prompt)

    # Build cited sources list
    cited_sources = []
    for i, chunk in enumerate(state.get("reranked_results", []), 1):
        cited_sources.append({
            "index": i,
            "chunk_id": chunk["chunk_id"],
            "source_type": chunk["source_type"],
            "product": chunk["product"],
            "text": chunk["text"],
            "reranker_score": chunk.get("reranker_score", 0.0),
        })

    return {
        "draft_response": response_text,
        "cited_sources": cited_sources,
    }


# =========================================================================
# Node 8: Format Response
# =========================================================================
async def format_response(state: CopilotState) -> dict:
    """Clean and validate the final response.

    This is a pass-through for now — the response is already structured.
    In production, this would validate citation markers and sanitize output.
    """
    return {}  # No state changes needed; output is already clean


# =========================================================================
# Prompt Builder
# =========================================================================
def _get_contact_block(ticket_text: str) -> str:
    """Build a contact info block to embed in the LLM prompt."""
    product = get_contact_for_query(ticket_text)
    if not product or product not in CONTACTS:
        return ""

    info = CONTACTS[product]
    return (
        f"\nRELEVANT CONTACT INFORMATION (include in your response):\n"
        f"Department: {info['department']}\n"
        f"Email: {info['email']}\n"
        f"Phone: {info['phone']}\n"
        f"Hours: {info['hours']}\n"
    )


def _build_prompt(state: CopilotState) -> str:
    """Construct the LLM prompt with context, history, and instructions."""

    contact_block = _get_contact_block(state["ticket_text"])

    # Handle empty retrieval
    if state.get("retrieval_empty") or not state.get("reranked_results"):
        return f"""You are a friendly, professional customer support agent for an e-commerce company that uses Shopify (storefront), Stripe (payments), Twilio (notifications), and Vercel (website hosting). The system found no relevant documentation for this issue. Write a warm, helpful response that:
1. Acknowledges the customer's issue with empathy
2. Asks clarifying questions to better understand the problem
3. Provides any general guidance you can
4. Assures them you'll help resolve it
5. Include the relevant department contact details if available

Never mention "retrieval system", "documentation database", or any internal system details.
{contact_block}
CUSTOMER MESSAGE: {state['ticket_text']}

YOUR RESPONSE:"""

    # Format retrieved chunks as numbered sources
    context_block = ""
    for i, chunk in enumerate(state["reranked_results"], 1):
        context_block += (
            f"[{i}] (Source: {chunk['source_type']}, Product: {chunk['product']})\n"
            f"{chunk['text']}\n\n"
        )

    # Format conversation history (last 3 turns = 6 messages)
    history_block = ""
    history = state.get("conversation_history", [])
    for msg in history[-6:]:
        role = "Customer" if msg["role"] == "user" else "Support Agent"
        history_block += f"{role}: {msg['content']}\n"

    escalation_note = ""
    if state.get("escalated"):
        escalation_note = (
            "\nNOTE: This ticket has low confidence and will be reviewed by a human agent. "
            "Provide your best draft response, and mention that a specialist will follow up.\n"
        )

    return f"""You are a friendly, knowledgeable customer support agent for an e-commerce company. Your company uses:
- **Shopify** for the online store (products, orders, shipping, themes)
- **Stripe** for payment processing (charges, refunds, subscriptions, payouts)
- **Twilio** for customer notifications (SMS, 2FA, voice calls)
- **Vercel** for website hosting and deployment

Write a response that a NON-TECHNICAL customer can understand and act on.

CRITICAL RULES — READ CAREFULLY:
1. AUDIENCE: The customer is an END USER — they do NOT have access to databases, servers, or command-line tools. Write for them accordingly.
2. TONE: Warm, professional, and empathetic. Start with a brief acknowledgment of their issue (1 sentence max, no filler).
3. PLAIN LANGUAGE: Explain the issue in simple terms. Avoid jargon without explaining it.
4. ACTIONABLE STEPS: Only suggest things the CUSTOMER can actually do:
   - Check their account/order/payment settings in the store UI
   - Try clearing browser cache / using incognito mode
   - Contact their bank or payment provider if needed
   - Reach out to a specific department for further help
5. TECHNICAL DETAILS (if needed): If the fix requires a developer or admin, put technical steps in a separate section labeled "**For your technical team:**" so the customer can forward it.
6. CONTACT INFO: If department contact details are provided below, include them at the end of your response so the customer knows who to reach for further help.
7. NEVER do these:
   - Never show raw SQL, CLI commands, or code in the main response body
   - Never say "Based on the retrieved context" or mention internal systems
   - Never assume the customer has admin or developer access
8. CITATIONS: Cite sources using [1], [2], etc. from the numbered references below. Keep citations subtle.
9. LENGTH: Keep the customer-facing part under 200 words. Technical team section can be longer if needed.
{escalation_note}
{contact_block}
INTERNAL KNOWLEDGE BASE (not visible to customer):
{context_block}

{f"PRIOR CONVERSATION:{chr(10)}{history_block}" if history_block else ""}

CUSTOMER MESSAGE:
{state['ticket_text']}

YOUR RESPONSE:"""
