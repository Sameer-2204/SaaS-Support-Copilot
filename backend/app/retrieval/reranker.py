"""Cross-encoder reranking and confidence scoring.

Uses cross-encoder/ms-marco-MiniLM-L-6-v2 to rerank fused retrieval
candidates. The cross-encoder processes (query, passage) pairs jointly,
producing relevance logits that are more accurate than bi-encoder similarity.

Confidence is computed as the sigmoid-normalized mean of the top-3 scores.
"""

import asyncio
import numpy as np
from sentence_transformers import CrossEncoder


class Reranker:
    """Cross-encoder reranker with confidence scoring."""

    _instance = None

    def __new__(cls, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if self._initialized:
            return
        self.model = CrossEncoder(model_name, max_length=512)
        self._initialized = True
        print(f"Reranker loaded: {model_name}")

    def rerank(
        self, query: str, candidates: list[dict], top_k: int = 5
    ) -> list[dict]:
        """Rerank candidates using the cross-encoder.

        Args:
            query: The query / ticket text.
            candidates: List of candidate chunk dicts (must have 'text' field).
            top_k: Number of top results to return after reranking.

        Returns:
            Top-k candidates sorted by cross-encoder score (descending).
            Each candidate gets a 'reranker_score' field added.
        """
        if not candidates:
            return []

        # Cross-encoder expects list of [query, passage] pairs
        pairs = [[query, c["text"]] for c in candidates]
        scores = self.model.predict(pairs)

        # Attach scores
        for i, candidate in enumerate(candidates):
            candidate["reranker_score"] = float(scores[i])

        # Sort by score descending and take top_k
        candidates.sort(key=lambda x: x["reranker_score"], reverse=True)
        return candidates[:top_k]

    async def arerank(
        self, query: str, candidates: list[dict], top_k: int = 5
    ) -> list[dict]:
        """Async wrapper for reranking (runs in thread pool)."""
        return await asyncio.to_thread(self.rerank, query, candidates, top_k)

    def compute_confidence(self, reranked_results: list[dict]) -> float:
        """Compute a confidence score from reranker outputs.

        Strategy: Use the mean of the top-3 reranker scores, passed through
        a sigmoid to normalize to [0, 1].

        The cross-encoder produces raw logits (typically in range [-10, +10]).
        Sigmoid normalization maps these to a probability-like confidence.
        Using top-3 mean (not just top-1) penalizes queries where only one
        document weakly matches.

        Args:
            reranked_results: List of reranked candidates with 'reranker_score'.

        Returns:
            Float in [0, 1] representing retrieval confidence.
        """
        if not reranked_results:
            return 0.0

        top_scores = [r["reranker_score"] for r in reranked_results[:3]]
        mean_score = np.mean(top_scores)

        # Sigmoid normalization
        confidence = 1.0 / (1.0 + np.exp(-mean_score))
        return round(float(confidence), 4)
