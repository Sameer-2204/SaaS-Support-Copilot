"""Embedding wrapper using all-MiniLM-L6-v2 via sentence-transformers ONNX backend.

Uses ONNX Runtime for inference instead of PyTorch, reducing RAM from ~700MB
to ~300MB — fits comfortably on free cloud tiers (512MB).
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """Singleton-pattern embedding model wrapper (ONNX backend)."""

    _instance = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._initialized:
            return
        # backend="onnx" uses ONNX Runtime for inference instead of PyTorch
        # Cuts model RAM from ~180MB to ~90MB and removes PyTorch GPU overhead
        self.model = SentenceTransformer(model_name, backend="onnx")
        self.dimension = 384  # all-MiniLM-L6-v2 output dimension
        self._initialized = True
        print(f"Embedder loaded: {model_name} (dim={self.dimension}, backend=onnx)")

    def embed_batch(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """Embed a list of texts in batches.

        Args:
            texts: List of text strings to embed.
            batch_size: Number of texts per batch (64 is optimal for CPU).

        Returns:
            np.ndarray of shape (N, 384) with L2-normalized embeddings.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string.

        Args:
            query: Query text to embed.

        Returns:
            np.ndarray of shape (384,) with L2-normalized embedding.
        """
        return self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
