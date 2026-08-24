---
title: SaaS Support Copilot API
emoji: 🤖
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
short_description: RAG-powered e-commerce support ticket automation API
---

# SaaS Support Copilot — Backend API

FastAPI backend for the AI-powered e-commerce support copilot. Uses hybrid RAG (BM25 + pgvector + Cross-Encoder reranking) with LangGraph orchestration and Groq LLM.

## Stack
- **FastAPI** — REST API
- **LangGraph** — Agent state machine
- **pgvector** — Vector search (Supabase)
- **Rank-BM25** — Keyword search
- **sentence-transformers** — Embeddings + reranking
- **Groq** — LLM inference

## Endpoints
- `GET /api/health` — Health check
- `POST /api/tickets` — Submit support ticket
- `GET /api/dashboard/stats` — Dashboard metrics
- `POST /api/feedback` — Submit feedback
