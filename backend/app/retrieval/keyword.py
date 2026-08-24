"""BM25 keyword search over the in-memory index.

Queries are tokenized and scored against the pre-built BM25Okapi index.
Results are filtered by source type and enriched with chunk metadata.
"""

from app.embeddings.bm25_index import tokenize


def bm25_search(
    query: str,
    bm25,
    chunk_ids: list[str],
    chunks_lookup: dict[str, dict],
    source_types: list[str],
    top_k: int = 20,
) -> list[dict]:
    """Search the BM25 index for keyword-relevant chunks.

    Args:
        query: The support ticket / query text.
        bm25: The BM25Okapi index object (from app.state).
        chunk_ids: Parallel list of chunk_ids matching BM25 index positions.
        chunks_lookup: Dict mapping chunk_id → full chunk metadata dict.
        source_types: List of source_type values to filter by.
        top_k: Number of results to return.

    Returns:
        List of result dicts with chunk data and bm25_score.
    """
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    # Pair scores with chunk_ids and filter by source type
    scored = []
    for i in range(len(scores)):
        cid = chunk_ids[i]
        chunk = chunks_lookup.get(cid)
        if chunk is None:
            continue
        if chunk.get("source_type") not in source_types:
            continue
        if scores[i] <= 0:
            continue
        scored.append((cid, float(scores[i])))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:top_k]

    return [
        {
            "chunk_id": cid,
            "source_type": chunks_lookup[cid]["source_type"],
            "document_id": chunks_lookup[cid]["document_id"],
            "product": chunks_lookup[cid]["product"],
            "text": chunks_lookup[cid]["text"],
            "bm25_score": score,
        }
        for cid, score in top
    ]
