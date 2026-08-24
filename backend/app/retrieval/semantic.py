"""Semantic search against pgvector using cosine distance.

Queries are embedded with all-MiniLM-L6-v2 and compared against stored
embeddings using the HNSW index with cosine distance operator (<=>).
"""

import asyncio
from sqlalchemy import text as sql_text
from app.embeddings.embedder import Embedder
from app.models.database import async_session_factory


# Lazy-loaded singleton embedder
_embedder: Embedder | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


async def semantic_search(
    query: str,
    source_types: list[str],
    top_k: int = 20,
) -> list[dict]:
    """Search pgvector for semantically similar chunks.

    Args:
        query: The support ticket / query text.
        source_types: List of source_type values to filter by.
        top_k: Number of results to return.

    Returns:
        List of result dicts with chunk data and similarity_score.
    """
    embedder = _get_embedder()

    # Embed query (CPU-bound, run in thread to avoid blocking event loop)
    query_embedding = await asyncio.to_thread(embedder.embed_query, query)

    # Build source type filter
    source_filter = ", ".join(f"'{s}'" for s in source_types)

    query_sql = sql_text(f"""
        SELECT
            chunk_id,
            source_type,
            document_id,
            product,
            text,
            1 - (embedding <=> :embedding::vector) AS similarity_score
        FROM document_chunks
        WHERE source_type IN ({source_filter})
        ORDER BY embedding <=> :embedding::vector
        LIMIT :top_k
    """)

    async with async_session_factory() as session:
        result = await session.execute(query_sql, {
            "embedding": str(query_embedding.tolist()),
            "top_k": top_k,
        })
        rows = result.fetchall()

    return [
        {
            "chunk_id": row.chunk_id,
            "source_type": row.source_type,
            "document_id": row.document_id,
            "product": row.product,
            "text": row.text,
            "semantic_score": float(row.similarity_score),
        }
        for row in rows
    ]
