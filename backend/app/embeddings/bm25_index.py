"""BM25 keyword search index using rank_bm25.

Build, save, and load the BM25 index for keyword-based retrieval.
The index is persisted to disk with joblib for fast server restarts.
"""

import re
import os
import joblib
from rank_bm25 import BM25Okapi
from typing import Optional


BM25_INDEX_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "bm25_index.pkl"
)


def tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer with basic cleaning.

    Keeps alphanumeric chars, hyphens, underscores, and dots.
    Suitable for technical support content.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-_.]", "", text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1]  # Skip single-char tokens


def build_bm25_index(chunks: list[dict]) -> tuple[BM25Okapi, list[str]]:
    """Build a BM25 index over all chunk texts.

    Args:
        chunks: List of chunk dicts with 'text' and 'chunk_id' fields.

    Returns:
        bm25: The BM25Okapi index object.
        chunk_ids: Parallel list of chunk_ids matching index positions.
    """
    corpus = [tokenize(c["text"]) for c in chunks]
    chunk_ids = [c["chunk_id"] for c in chunks]

    bm25 = BM25Okapi(corpus)
    print(f"BM25 index built over {len(corpus)} documents")
    return bm25, chunk_ids


def save_bm25_index(
    bm25: BM25Okapi,
    chunk_ids: list[str],
    path: Optional[str] = None,
):
    """Persist BM25 index and chunk_id mapping to disk."""
    path = path or BM25_INDEX_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump({"bm25": bm25, "chunk_ids": chunk_ids}, path)
    print(f"BM25 index saved to {path}")


def load_bm25_index(path: Optional[str] = None) -> tuple[BM25Okapi, list[str]]:
    """Load a persisted BM25 index from disk.

    Returns:
        bm25: The BM25Okapi index object.
        chunk_ids: Parallel list of chunk_ids.
    """
    path = path or BM25_INDEX_PATH
    data = joblib.load(path)
    print(f"BM25 index loaded from {path}: {len(data['chunk_ids'])} documents")
    return data["bm25"], data["chunk_ids"]
