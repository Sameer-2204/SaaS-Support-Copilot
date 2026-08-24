"""Chunking logic for support content.

Uses recursive character splitting with Markdown-aware boundaries.
- Max chunk size: ~512 tokens (~2000 chars for English)
- Overlap: ~50 tokens (~200 chars)
- Split priority: headings > paragraphs > newlines > sentences
"""

import re
from typing import Optional

# Boundary patterns in priority order (most meaningful first)
SPLIT_PATTERNS = [
    r'\n#{1,3} ',       # Markdown headings (h1-h3)
    r'\n\n',            # Double newline (paragraph break)
    r'\n',              # Single newline
    r'(?<=\.)\s+',      # Sentence boundary (after period)
]

MAX_CHUNK_CHARS = 2000   # ~512 tokens at ~4 chars/token for English
OVERLAP_CHARS = 200      # ~50 tokens
MIN_CHUNK_CHARS = 50     # Skip fragments shorter than this


def chunk_text(text: str, doc_metadata: dict) -> list[dict]:
    """Split text into chunks respecting Markdown structure.

    Args:
        text: The full text to chunk.
        doc_metadata: Dict with at least 'id', 'source_type', 'product', 'timestamp'.

    Returns:
        List of chunk dicts with metadata and text.
    """
    chunks = []
    segments = _recursive_split(text, max_size=MAX_CHUNK_CHARS)

    for i, segment in enumerate(segments):
        segment = segment.strip()
        if len(segment) < MIN_CHUNK_CHARS:
            continue
        chunks.append({
            **doc_metadata,
            "chunk_id": f"{doc_metadata['id']}_chunk_{i:03d}",
            "chunk_index": i,
            "text": segment,
            "char_count": len(segment),
        })
    return chunks


def chunk_document(doc: dict) -> list[dict]:
    """Convenience: chunk a document dict that has 'full_text' and metadata fields."""
    metadata = {
        "id": doc["id"],
        "source_type": doc["source_type"],
        "product": doc.get("product", "general"),
        "timestamp": doc.get("timestamp", "2024-01-01"),
    }
    return chunk_text(doc["full_text"], metadata)


def _recursive_split(text: str, max_size: int) -> list[str]:
    """Try each split pattern in priority order until chunks are small enough."""
    if len(text) <= max_size:
        return [text]

    for pattern in SPLIT_PATTERNS:
        parts = re.split(pattern, text)
        if len(parts) <= 1:
            continue

        # Recombine parts that are small enough
        result = []
        current = ""
        for part in parts:
            if len(current) + len(part) <= max_size:
                current += part
            else:
                if current:
                    result.append(current)
                current = part
        if current:
            result.append(current)

        # Recursively split any still-too-large chunks
        final = []
        for chunk in result:
            if len(chunk) > max_size:
                final.extend(_recursive_split(chunk, max_size))
            else:
                final.append(chunk)

        # Add overlap between adjacent chunks
        return _add_overlap(final)

    # Fallback: hard split at max_size with overlap
    return _hard_split(text, max_size)


def _add_overlap(chunks: list[str]) -> list[str]:
    """Prepend the last OVERLAP_CHARS of the previous chunk to each subsequent chunk."""
    if len(chunks) <= 1:
        return chunks
    result = [chunks[0]]
    for i in range(1, len(chunks)):
        overlap = chunks[i - 1][-OVERLAP_CHARS:]
        result.append(overlap + chunks[i])
    return result


def _hard_split(text: str, max_size: int) -> list[str]:
    """Last resort: split text at fixed intervals with overlap."""
    step = max_size - OVERLAP_CHARS
    return [text[i:i + max_size] for i in range(0, len(text), step)]
