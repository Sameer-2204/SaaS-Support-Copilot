"""Embedding wrapper using all-MiniLM-L6-v2 via sentence-transformers.

Provides batch embedding for corpus indexing and single-query embedding
for retrieval. All embeddings are L2-normalized for cosine similarity
via inner product.
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """Singleton-pattern embedding model wrapper."""

    _instance = None

    def __new__(cls, model_name: str = "all-MiniLM-L6-v2"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._initialized:
            return
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()  # 384
        self._initialized = True
        print(f"Embedder loaded: {model_name} (dim={self.dimension})")

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
