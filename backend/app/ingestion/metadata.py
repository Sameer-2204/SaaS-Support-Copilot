"""Metadata assignment for document chunks.

Ensures every chunk has a consistent metadata schema
regardless of its source type.
"""

from datetime import datetime


VALID_SOURCE_TYPES = {"resolved_ticket", "product_docs", "changelog", "api_error"}


def assign_metadata(chunk: dict) -> dict:
    """Normalize and validate chunk metadata.

    Args:
        chunk: Raw chunk dict from the chunker.

    Returns:
        Cleaned chunk dict with all required metadata fields.
    """
    source_type = chunk.get("source_type", "product_docs")
    if source_type not in VALID_SOURCE_TYPES:
        source_type = "product_docs"

    return {
        "chunk_id": chunk["chunk_id"],
        "source_type": source_type,
        "document_id": chunk["id"],
        "product": chunk.get("product", "general"),
        "timestamp": chunk.get("timestamp", datetime.now().strftime("%Y-%m-%d")),
        "text": chunk["text"],
        "chunk_index": chunk.get("chunk_index", 0),
        "char_count": chunk.get("char_count", len(chunk["text"])),
    }


def enrich_all_chunks(chunks: list[dict]) -> list[dict]:
    """Apply metadata normalization to a list of chunks."""
    return [assign_metadata(c) for c in chunks]
