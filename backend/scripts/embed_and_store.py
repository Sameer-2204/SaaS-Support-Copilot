"""Embed all processed chunks and store in pgvector.

Usage:
    python -m scripts.embed_and_store
"""

import json
import os
import sys
import asyncio
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import text
from app.embeddings.embedder import Embedder
from app.models.database import async_session_factory


DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "processed", "all_chunks.json"
)


async def embed_and_store(data_path: str = DATA_PATH, batch_size: int = 64):
    """Embed all chunks and insert into pgvector."""

    # Load chunks
    with open(data_path, encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {data_path}")

    # Embed
    embedder = Embedder()
    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks (batch_size={batch_size})...")
    embeddings = embedder.embed_batch(texts, batch_size=batch_size)
    print(f"Embeddings shape: {embeddings.shape}")

    # Store in pgvector
    print("Storing embeddings in pgvector...")
    insert_sql = text("""
        INSERT INTO document_chunks
            (chunk_id, source_type, document_id, product, timestamp, text, embedding)
        VALUES
            (:chunk_id, :source_type, :document_id, :product, :timestamp, :text, :embedding)
        ON CONFLICT (chunk_id) DO UPDATE SET
            embedding = EXCLUDED.embedding,
            text = EXCLUDED.text
    """)

    inserted = 0
    async with async_session_factory() as session:
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            # asyncpg requires a date object (not string) for DATE columns
            ts_str = chunk.get("timestamp")
            try:
                ts = date.fromisoformat(ts_str) if ts_str else None
            except ValueError:
                ts = None

            await session.execute(insert_sql, {
                "chunk_id": chunk["chunk_id"],
                "source_type": chunk["source_type"],
                "document_id": chunk["document_id"],
                "product": chunk["product"],
                "timestamp": ts,
                "text": chunk["text"],
                "embedding": str(emb.tolist()),
            })
            inserted += 1

            if (i + 1) % 100 == 0:
                await session.commit()
                print(f"  Inserted {i + 1}/{len(chunks)}")

        await session.commit()

    print(f"\n✅ Stored {inserted} chunks with embeddings in pgvector")


if __name__ == "__main__":
    asyncio.run(embed_and_store())
