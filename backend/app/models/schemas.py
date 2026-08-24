"""Pydantic request/response schemas for all API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ===================================================================
# POST /api/tickets
# ===================================================================
class TicketRequest(BaseModel):
    """Request schema for submitting a support ticket."""
    ticket_text: str = Field(
        ..., min_length=10, max_length=5000,
        description="The support ticket text"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for follow-up questions (auto-generated if not provided)"
    )


class CitedSource(BaseModel):
    """A single cited source in the response."""
    index: int
    chunk_id: str
    source_type: str
    product: str
    text: str
    reranker_score: float


class TicketResponse(BaseModel):
    """Response schema for a processed support ticket."""
    ticket_id: str
    draft_response: str
    cited_sources: list[CitedSource]
    confidence_score: float
    escalated: bool
    escalation_reason: Optional[str] = None
    routed_sources: list[str]
    session_id: str
    processing_time_ms: float
    created_at: datetime


# ===================================================================
# GET /api/dashboard/stats
# ===================================================================
class DashboardStats(BaseModel):
    """Aggregate dashboard statistics."""
    total_tickets: int
    auto_resolved: int
    escalated: int
    auto_resolved_pct: float
    escalated_pct: float
    avg_confidence: float
    avg_processing_time_ms: float
    category_distribution: dict[str, int]
    confidence_over_time: list[dict]


# ===================================================================
# GET /api/dashboard/history
# ===================================================================
class TicketHistoryItem(BaseModel):
    """A single ticket in the history list."""
    ticket_id: str
    ticket_text: str
    confidence_score: float
    escalated: bool
    routed_sources: list[str]
    processing_time_ms: float
    created_at: datetime


class TicketHistoryResponse(BaseModel):
    """Paginated ticket history."""
    items: list[TicketHistoryItem]
    total: int
    page: int
    limit: int


# ===================================================================
# GET /api/visualize/umap
# ===================================================================
class UmapPoint(BaseModel):
    """A single point in the UMAP projection."""
    x: float
    y: float
    chunk_id: str
    source_type: str
    product: str
    text_preview: str


class UmapResponse(BaseModel):
    """UMAP projection of document embeddings."""
    points: list[UmapPoint]


# ===================================================================
# GET /api/health
# ===================================================================
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    chunks_indexed: int
    bm25_loaded: bool


# ===================================================================
# POST /api/feedback — Submit feedback on a response
# ===================================================================
class FeedbackRequest(BaseModel):
    """Request schema for submitting feedback on a copilot response."""
    ticket_id: str = Field(..., description="The ticket ID this feedback is for")
    rating: int = Field(
        ..., ge=1, le=5,
        description="Rating from 1 (very unsatisfied) to 5 (very satisfied)"
    )
    comment: Optional[str] = Field(
        default=None, max_length=2000,
        description="Optional written feedback"
    )
    was_helpful: bool = Field(
        ..., description="Whether the response solved the customer's issue"
    )


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""
    feedback_id: str
    ticket_id: str
    rating: int
    comment: Optional[str] = None
    was_helpful: bool
    created_at: datetime


# ===================================================================
# GET /api/contacts/{product} — Department contact info
# ===================================================================
class ContactInfo(BaseModel):
    """Contact information for a department."""
    department: str
    email: str
    phone: str
    hours: str
    specialties: list[str]


# ===================================================================
# GET /api/dashboard/feedback-summary — Feedback analytics
# ===================================================================
class FeedbackSummary(BaseModel):
    """Aggregate feedback statistics for the dashboard."""
    total_feedback: int
    avg_rating: float
    satisfaction_rate: float  # % of was_helpful=True
    rating_distribution: dict[str, int]  # {"1": count, "2": count, ...}
    recent_feedback: list[FeedbackResponse]
