"""FastAPI application entry point.

Serves the SaaS Support Copilot RAG pipeline via REST endpoints.
On startup, loads BM25 index and chunks lookup into memory.
"""

import json
import os
import time
import uuid
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.schemas import (
    TicketRequest,
    TicketResponse,
    CitedSource,
    DashboardStats,
    TicketHistoryItem,
    TicketHistoryResponse,
    UmapResponse,
    UmapPoint,
    HealthResponse,
    FeedbackRequest,
    FeedbackResponse,
    FeedbackSummary,
    ContactInfo,
)
from app.graph.builder import copilot_graph
from app.graph.nodes import get_history, save_turn, set_bm25_state
from app.middleware.logging import RequestLoggingMiddleware
from app.utils.umap_utils import compute_umap_projection
from app.embeddings.bm25_index import load_bm25_index


# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("saas_copilot")


# --- In-memory stores ---
_ticket_history: dict[str, dict] = {}
_feedback_store: dict[str, dict] = {}  # feedback_id -> feedback data
_ticket_feedback: dict[str, str] = {}  # ticket_id -> feedback_id

# --- Load contacts ---
_contacts_path = os.path.join(os.path.dirname(__file__), "..", "data", "contacts.json")
try:
    with open(_contacts_path, encoding="utf-8") as _cf:
        _contacts = json.load(_cf)
except (FileNotFoundError, json.JSONDecodeError):
    _contacts = {}


# --- App Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load BM25 index and chunks lookup on startup."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    bm25_path = os.path.join(data_dir, "bm25_index.pkl")
    lookup_path = os.path.join(data_dir, "chunks_lookup.json")

    # Load BM25 index
    bm25_loaded = False
    chunks_count = 0
    try:
        bm25, chunk_ids = load_bm25_index(bm25_path)
        chunks_count = len(chunk_ids)

        # Load chunks lookup
        with open(lookup_path, encoding="utf-8") as f:
            chunks_lookup = json.load(f)

        # Inject into graph nodes
        set_bm25_state(bm25, chunk_ids, chunks_lookup)
        bm25_loaded = True
        logger.info(f"BM25 index loaded: {chunks_count} chunks")
    except FileNotFoundError:
        logger.warning("BM25 index not found. Run scripts/build_bm25.py first.")
    except Exception as e:
        logger.error(f"Failed to load BM25 index: {e}")

    app.state.bm25_loaded = bm25_loaded
    app.state.chunks_count = chunks_count

    yield

    logger.info("Shutting down")


# --- App Instance ---
app = FastAPI(
    title="SaaS Support Copilot",
    description="AI-powered support ticket automation with RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Logging ---
app.add_middleware(RequestLoggingMiddleware)


# ===================================================================
# POST /api/tickets — Submit a support ticket
# ===================================================================
@app.post("/api/tickets", response_model=TicketResponse)
async def process_ticket(request: TicketRequest):
    """Process a support ticket through the RAG pipeline."""
    start = time.time()
    session_id = request.session_id or str(uuid.uuid4())
    ticket_id = str(uuid.uuid4())

    # Build initial state
    initial_state = {
        "ticket_text": request.ticket_text,
        "session_id": session_id,
        "conversation_history": get_history(session_id),
        "routed_sources": [],
        "semantic_results": [],
        "bm25_results": [],
        "fused_results": [],
        "reranked_results": [],
        "confidence_score": 0.0,
        "escalated": False,
        "escalation_reason": "",
        "draft_response": "",
        "cited_sources": [],
        "error": None,
        "retrieval_empty": False,
    }

    try:
        # Run the LangGraph pipeline
        result = await copilot_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    # Save conversation turn for follow-ups
    save_turn(session_id, request.ticket_text, result.get("draft_response", ""))

    processing_time = (time.time() - start) * 1000

    # Build response
    cited_sources = [
        CitedSource(**src) for src in result.get("cited_sources", [])
    ]

    response = TicketResponse(
        ticket_id=ticket_id,
        draft_response=result.get("draft_response", ""),
        cited_sources=cited_sources,
        confidence_score=result.get("confidence_score", 0.0),
        escalated=result.get("escalated", False),
        escalation_reason=result.get("escalation_reason"),
        routed_sources=result.get("routed_sources", []),
        session_id=session_id,
        processing_time_ms=round(processing_time, 2),
        created_at=datetime.now(),
    )

    # Store in history for dashboard
    _ticket_history[ticket_id] = {
        "ticket_id": ticket_id,
        "ticket_text": request.ticket_text,
        "confidence_score": response.confidence_score,
        "escalated": response.escalated,
        "routed_sources": response.routed_sources,
        "processing_time_ms": processing_time,
        "created_at": response.created_at,
    }

    return response


# ===================================================================
# GET /api/tickets/{ticket_id} — Get a processed ticket by ID
# ===================================================================
@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Retrieve a previously processed ticket result."""
    if ticket_id not in _ticket_history:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return _ticket_history[ticket_id]


# ===================================================================
# GET /api/dashboard/stats — Dashboard statistics
# ===================================================================
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Aggregate statistics across all processed tickets."""
    tickets = list(_ticket_history.values())
    total = len(tickets)

    if total == 0:
        return DashboardStats(
            total_tickets=0,
            auto_resolved=0,
            escalated=0,
            auto_resolved_pct=0.0,
            escalated_pct=0.0,
            avg_confidence=0.0,
            avg_processing_time_ms=0.0,
            category_distribution={},
            confidence_over_time=[],
        )

    escalated_count = sum(1 for t in tickets if t["escalated"])
    resolved_count = total - escalated_count

    # Category distribution (by primary routed source)
    category_dist: dict[str, int] = defaultdict(int)
    for t in tickets:
        for src in t.get("routed_sources", []):
            category_dist[src] += 1

    # Confidence over time (grouped by date)
    date_groups: dict[str, list[float]] = defaultdict(list)
    for t in tickets:
        date_str = t["created_at"].strftime("%Y-%m-%d")
        date_groups[date_str].append(t["confidence_score"])

    confidence_over_time = [
        {
            "date": date,
            "avg_confidence": round(sum(scores) / len(scores), 4),
            "count": len(scores),
        }
        for date, scores in sorted(date_groups.items())
    ]

    return DashboardStats(
        total_tickets=total,
        auto_resolved=resolved_count,
        escalated=escalated_count,
        auto_resolved_pct=round(resolved_count / total * 100, 1),
        escalated_pct=round(escalated_count / total * 100, 1),
        avg_confidence=round(sum(t["confidence_score"] for t in tickets) / total, 4),
        avg_processing_time_ms=round(
            sum(t["processing_time_ms"] for t in tickets) / total, 2
        ),
        category_distribution=dict(category_dist),
        confidence_over_time=confidence_over_time,
    )


# ===================================================================
# GET /api/dashboard/history — Paginated ticket history
# ===================================================================
@app.get("/api/dashboard/history", response_model=TicketHistoryResponse)
async def get_ticket_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Paginated list of past ticket results."""
    all_tickets = sorted(
        _ticket_history.values(),
        key=lambda t: t["created_at"],
        reverse=True,
    )
    total = len(all_tickets)
    start = (page - 1) * limit
    end = start + limit
    page_items = all_tickets[start:end]

    return TicketHistoryResponse(
        items=[TicketHistoryItem(**t) for t in page_items],
        total=total,
        page=page,
        limit=limit,
    )


# ===================================================================
# GET /api/visualize/umap — UMAP embedding projection
# ===================================================================
@app.get("/api/visualize/umap", response_model=UmapResponse)
async def get_umap_projection():
    """UMAP 2D projection of all document embeddings."""
    try:
        points = await compute_umap_projection()
        return UmapResponse(
            points=[UmapPoint(**p) for p in points]
        )
    except Exception as e:
        logger.error(f"UMAP projection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"UMAP projection failed: {str(e)}"
        )


# ===================================================================
# GET /api/health — Health check
# ===================================================================
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway deployment monitoring."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        chunks_indexed=getattr(app.state, "chunks_count", 0),
        bm25_loaded=getattr(app.state, "bm25_loaded", False),
    )


# ===================================================================
# POST /api/feedback — Submit feedback on a response
# ===================================================================
@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit customer feedback/rating for a copilot response."""
    # Verify ticket exists
    if request.ticket_id not in _ticket_history:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Check if feedback already submitted for this ticket
    if request.ticket_id in _ticket_feedback:
        raise HTTPException(
            status_code=409,
            detail="Feedback already submitted for this ticket"
        )

    feedback_id = str(uuid.uuid4())
    feedback_data = {
        "feedback_id": feedback_id,
        "ticket_id": request.ticket_id,
        "rating": request.rating,
        "comment": request.comment,
        "was_helpful": request.was_helpful,
        "created_at": datetime.now(),
    }

    _feedback_store[feedback_id] = feedback_data
    _ticket_feedback[request.ticket_id] = feedback_id

    logger.info(
        f"Feedback received: ticket={request.ticket_id} "
        f"rating={request.rating} helpful={request.was_helpful}"
    )

    return FeedbackResponse(**feedback_data)


# ===================================================================
# GET /api/feedback/summary — Feedback analytics for dashboard
# ===================================================================
@app.get("/api/feedback/summary", response_model=FeedbackSummary)
async def get_feedback_summary():
    """Aggregate feedback statistics."""
    feedbacks = list(_feedback_store.values())
    total = len(feedbacks)

    if total == 0:
        return FeedbackSummary(
            total_feedback=0,
            avg_rating=0.0,
            satisfaction_rate=0.0,
            rating_distribution={str(i): 0 for i in range(1, 6)},
            recent_feedback=[],
        )

    avg_rating = sum(f["rating"] for f in feedbacks) / total
    helpful_count = sum(1 for f in feedbacks if f["was_helpful"])
    satisfaction_rate = round(helpful_count / total * 100, 1)

    # Rating distribution
    dist = {str(i): 0 for i in range(1, 6)}
    for f in feedbacks:
        dist[str(f["rating"])] += 1

    # Recent feedback (last 10)
    recent = sorted(feedbacks, key=lambda f: f["created_at"], reverse=True)[:10]

    return FeedbackSummary(
        total_feedback=total,
        avg_rating=round(avg_rating, 2),
        satisfaction_rate=satisfaction_rate,
        rating_distribution=dist,
        recent_feedback=[FeedbackResponse(**f) for f in recent],
    )


# ===================================================================
# GET /api/contacts/{product} — Department contact info
# ===================================================================
@app.get("/api/contacts/{product}", response_model=ContactInfo)
async def get_contact_info(product: str):
    """Get department contact info for a specific product/platform."""
    product = product.lower()
    if product not in _contacts:
        raise HTTPException(
            status_code=404,
            detail=f"No contact info for '{product}'. Valid: {list(_contacts.keys())}"
        )
    return ContactInfo(**_contacts[product])


# ===================================================================
# GET /api/contacts — All department contacts
# ===================================================================
@app.get("/api/contacts")
async def get_all_contacts():
    """Get all department contact information."""
    return _contacts
