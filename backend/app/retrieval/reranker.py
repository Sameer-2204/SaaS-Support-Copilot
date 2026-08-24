"""Cross-encoder reranking and confidence scoring via ONNX Runtime.

Uses optimum's ORTModelForSequenceClassification to run inference through
ONNX Runtime instead of PyTorch. This eliminates ~120MB of model weight
memory from torch, fitting the full stack within 512MB free tier limits.
"""

import os
import asyncio
import numpy as np
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSequenceClassification


# Pre-exported ONNX path (baked into Docker image at build time)
_ONNX_CACHE = os.path.join(
    os.environ.get("SENTENCE_TRANSFORMERS_HOME", "/app/models_cache"),
    "cross-encoder-onnx",
)


class Reranker:
    """Cross-encoder reranker using ONNX Runtime for inference."""

    _instance = None

    def __new__(cls, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        if self._initialized:
            return

        if os.path.exists(_ONNX_CACHE):
            # Load from pre-exported ONNX cache (Docker image build-time artifact)
            self.tokenizer = AutoTokenizer.from_pretrained(_ONNX_CACHE)
            self.model = ORTModelForSequenceClassification.from_pretrained(_ONNX_CACHE)
            print(f"Reranker loaded from ONNX cache: {_ONNX_CACHE}")
        else:
            # Fallback: export from HuggingFace on first load (requires torch, ~30s)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = ORTModelForSequenceClassification.from_pretrained(
                model_name, export=True
            )
            print(f"Reranker loaded: {model_name} (exported to ONNX on-the-fly)")

        self._initialized = True

    def _score_pairs(self, pairs: list[list[str]]) -> np.ndarray:
        """Tokenize and score (query, passage) pairs via ONNX Runtime."""
        inputs = self.tokenizer(
            [p[0] for p in pairs],
            [p[1] for p in pairs],
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        outputs = self.model(**inputs)
        # logits shape is (N, 1) for cross-encoder — flatten to (N,)
        scores = outputs.logits.detach().numpy().flatten()
        return scores

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

        pairs = [[query, c["text"]] for c in candidates]
        scores = self._score_pairs(pairs)

        for i, candidate in enumerate(candidates):
            candidate["reranker_score"] = float(scores[i])

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
