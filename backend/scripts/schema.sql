-- pgvector setup for Supabase
-- Run this in the Supabase SQL Editor

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the document chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id              BIGSERIAL PRIMARY KEY,
    chunk_id        TEXT UNIQUE NOT NULL,
    source_type     TEXT NOT NULL,           -- 'resolved_ticket', 'product_docs', 'changelog', 'api_error'
    document_id     TEXT NOT NULL,
    product         TEXT NOT NULL DEFAULT 'general',
    timestamp       DATE,
    text            TEXT NOT NULL,
    embedding       vector(384) NOT NULL,    -- all-MiniLM-L6-v2 output dimension
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create indexes for filtered queries
CREATE INDEX IF NOT EXISTS idx_chunks_source_type ON document_chunks (source_type);
CREATE INDEX IF NOT EXISTS idx_chunks_product ON document_chunks (product);

-- 4. Create HNSW vector similarity index
--    m=16: neighbors per node (good balance for <100K vectors)
--    ef_construction=64: build-time effort (standard default)
--    vector_cosine_ops: correct for L2-normalized embeddings
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON document_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 5. Optional: table for storing ticket processing history (for dashboard)
CREATE TABLE IF NOT EXISTS ticket_history (
    id                  BIGSERIAL PRIMARY KEY,
    ticket_id           TEXT UNIQUE NOT NULL,
    ticket_text         TEXT NOT NULL,
    draft_response      TEXT NOT NULL,
    confidence_score    FLOAT NOT NULL,
    escalated           BOOLEAN NOT NULL DEFAULT FALSE,
    escalation_reason   TEXT,
    routed_sources      TEXT[] NOT NULL DEFAULT '{}',
    processing_time_ms  FLOAT NOT NULL DEFAULT 0,
    session_id          TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ticket_history_created ON ticket_history (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ticket_history_escalated ON ticket_history (escalated);
