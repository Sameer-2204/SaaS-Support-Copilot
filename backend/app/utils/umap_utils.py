"""UMAP projection utility for embedding space visualization.

Fetches all embeddings from pgvector, runs UMAP dimensionality reduction
to 2D, and returns the coordinates with metadata for the scatter plot.

Results are cached in memory since the projection doesn't change unless
documents are re-ingested.
"""

import numpy as np
from sqlalchemy import text as sql_text
from app.models.database import async_session_factory

# In-memory cache for UMAP results
_umap_cache: list[dict] | None = None


async def compute_umap_projection(force_recompute: bool = False) -> list[dict]:
    """Fetch embeddings from pgvector and project to 2D with UMAP.

    Args:
        force_recompute: If True, bypass the cache and recompute.

    Returns:
        List of UmapPoint-like dicts with x, y, chunk_id, source_type, product, text_preview.
    """
    global _umap_cache
    if _umap_cache is not None and not force_recompute:
        return _umap_cache

    # Fetch all embeddings
    async with async_session_factory() as session:
        result = await session.execute(
            sql_text(
                "SELECT chunk_id, source_type, product, "
                "LEFT(text, 100) as preview, embedding "
                "FROM document_chunks"
            )
        )
        rows = result.fetchall()

    if not rows:
        return []

    # Parse embeddings from pgvector format
    embeddings = []
    for row in rows:
        # pgvector returns embedding as a string like '[0.1, 0.2, ...]'
        emb_str = str(row.embedding)
        emb = list(map(float, emb_str.strip("[]").split(",")))
        embeddings.append(emb)

    embeddings_array = np.array(embeddings)

    # Import UMAP lazily (it's a heavy import)
    import umap

    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.1,
        random_state=42,
        metric="cosine",
    )
    coords = reducer.fit_transform(embeddings_array)

    # Build result
    points = [
        {
            "x": float(coords[i, 0]),
            "y": float(coords[i, 1]),
            "chunk_id": rows[i].chunk_id,
            "source_type": rows[i].source_type,
            "product": rows[i].product,
            "text_preview": rows[i].preview or "",
        }
        for i in range(len(rows))
    ]

    # Cache the result
    _umap_cache = points
    return points
