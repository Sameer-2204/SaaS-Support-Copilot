"""Full ingestion pipeline: load → chunk → metadata → save processed chunks.

Usage:
    python -m scripts.ingest
"""

import json
import os
import sys

# Add parent dir to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ingestion.loader import (
    load_support_dialogues,
    load_markdown_docs,
    load_changelogs,
    load_api_errors,
    load_resolved_tickets_json,
    load_product_docs_json,
)
from app.ingestion.chunker import chunk_document
from app.ingestion.metadata import enrich_all_chunks


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "processed", "all_chunks.json")


def run_ingestion():
    """Run the full ingestion pipeline across all sources."""
    all_docs = []

    # 1. Load resolved tickets from JSON
    print("\n=== Loading resolved tickets ===")
    tickets = load_resolved_tickets_json()
    all_docs.extend(tickets)
    print(f"  → {len(tickets)} resolved tickets")

    # 1b. Also try HuggingFace dataset (optional, may not be available)
    print("\n=== Loading HuggingFace support dialogues (optional) ===")
    try:
        hf_tickets = load_support_dialogues()
        all_docs.extend(hf_tickets)
        print(f"  → {len(hf_tickets)} HuggingFace tickets")
    except Exception as e:
        print(f"  ⚠ Skipping HuggingFace dataset: {e}")

    # 2. Load product docs from JSON (Shopify, Stripe, Twilio, Vercel)
    print("\n=== Loading product documentation ===")
    prod_docs = load_product_docs_json()
    all_docs.extend(prod_docs)
    print(f"  → {len(prod_docs)} product docs")

    # 3. Load changelogs
    print("\n=== Loading changelogs ===")
    changelogs = load_changelogs()
    all_docs.extend(changelogs)
    print(f"  → {len(changelogs)} changelog entries")

    # 4. Load API error references
    print("\n=== Loading API error references ===")
    api_errors = load_api_errors()
    all_docs.extend(api_errors)
    print(f"  → {len(api_errors)} API error references")

    print(f"\n=== Total documents loaded: {len(all_docs)} ===")

    # 5. Chunk all documents
    print("\n=== Chunking documents ===")
    all_chunks = []
    for doc in all_docs:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
    print(f"  → {len(all_chunks)} chunks created")

    # 6. Enrich metadata
    print("\n=== Enriching metadata ===")
    all_chunks = enrich_all_chunks(all_chunks)

    # 7. Save processed chunks
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved {len(all_chunks)} chunks to {OUTPUT_PATH}")

    # Print summary
    source_counts = {}
    for c in all_chunks:
        st = c["source_type"]
        source_counts[st] = source_counts.get(st, 0) + 1
    print("\nChunks by source type:")
    for st, count in sorted(source_counts.items()):
        print(f"  {st}: {count}")

    return all_chunks


if __name__ == "__main__":
    run_ingestion()
