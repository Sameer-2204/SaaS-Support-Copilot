"""Build and persist the BM25 index from processed chunks.

Usage:
    python -m scripts.build_bm25
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.embeddings.bm25_index import build_bm25_index, save_bm25_index


DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "processed", "all_chunks.json"
)


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Building BM25 index over {len(chunks)} chunks...")
    bm25, chunk_ids = build_bm25_index(chunks)
    save_bm25_index(bm25, chunk_ids)

    # Also save the chunks lookup for BM25 search
    chunks_lookup = {c["chunk_id"]: c for c in chunks}
    lookup_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "chunks_lookup.json"
    )
    with open(lookup_path, "w", encoding="utf-8") as f:
        json.dump(chunks_lookup, f, ensure_ascii=False)
    print(f"Chunks lookup saved to {lookup_path}")

    print(f"\n✅ BM25 index ready with {len(chunk_ids)} documents")


if __name__ == "__main__":
    main()
