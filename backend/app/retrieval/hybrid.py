"""Reciprocal Rank Fusion (RRF) for combining semantic + BM25 results.

RRF uses rank positions (not raw scores) to merge results from different
retrieval systems. This avoids the need for score normalization.

Formula: RRF_score = sum( 1 / (k + rank) ) across all systems
k=60 is the standard constant from Cormack, Clarke & Butt (2009).
"""


def reciprocal_rank_fusion(
    semantic_results: list[dict],
    bm25_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """Combine semantic and BM25 results using Reciprocal Rank Fusion.

    Args:
        semantic_results: Ranked results from semantic search.
        bm25_results: Ranked results from BM25 search.
        k: RRF constant (default 60).

    Returns:
        Merged and deduplicated results sorted by RRF score (descending).
    """
    rrf_scores: dict[str, float] = {}
    chunk_data: dict[str, dict] = {}

    # Score from semantic results (rank is 0-indexed, so rank+1 for 1-indexed)
    for rank, result in enumerate(semantic_results):
        cid = result["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
        chunk_data[cid] = result

    # Score from BM25 results
    for rank, result in enumerate(bm25_results):
        cid = result["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
        if cid not in chunk_data:
            chunk_data[cid] = result

    # Sort by fused score descending
    sorted_ids = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)

    return [
        {**chunk_data[cid], "rrf_score": rrf_scores[cid]}
        for cid in sorted_ids
    ]
