# 🤖 SaaS Support Copilot

> AI-powered support ticket automation with RAG, hybrid retrieval, and confidence-based escalation.

<!-- ![Demo](./assets/demo.gif) -->

A production-grade Retrieval-Augmented Generation system that accepts support tickets, retrieves relevant context from 4 knowledge sources, generates cited draft responses, and auto-escalates low-confidence tickets to human agents.

## ✨ Features

- **Hybrid Retrieval** — Combines semantic search (pgvector) + BM25 keyword search with Reciprocal Rank Fusion
- **Cross-Encoder Reranking** — ms-marco-MiniLM-L-6-v2 reranks candidates for precision
- **LLM-Generated Cited Responses** — LLaMA 3.1 8B via Groq generates responses with inline source citations
- **Confidence Scoring** — Sigmoid-normalized reranker scores drive auto-escalation decisions
- **4 Knowledge Sources** — Product docs, past resolved tickets, changelogs, and API error references
- **Interactive Dashboard** — Stats, confidence trends, and category distribution charts
- **Embedding Visualizer** — UMAP projection of the document corpus colored by source type
- **Conversation Follow-ups** — Session-aware context for multi-turn ticket conversations

## 🏗️ Architecture

```
┌──────────────┐       ┌──────────────────────────────────────────┐
│  React + TW  │──────►│  FastAPI (async)                        │
│  Vercel      │◄──────│  Railway                                │
└──────────────┘       │                                          │
                       │  ┌─────────────────────────────────┐    │
                       │  │  LangGraph Pipeline              │    │
                       │  │  classify → retrieve → fuse      │    │
                       │  │  → rerank → confidence → generate│    │
                       │  └─────────────────────────────────┘    │
                       │         │              │                 │
                       │    ┌────▼────┐   ┌─────▼──────┐         │
                       │    │pgvector │   │  BM25      │         │
                       │    │Supabase │   │  In-memory │         │
                       │    └─────────┘   └────────────┘         │
                       │         │                                │
                       │    ┌────▼────────────────────┐          │
                       │    │  Groq API (LLaMA 3.1)   │          │
                       │    └─────────────────────────┘          │
                       └──────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Tailwind CSS + shadcn/ui |
| Charts | Recharts (dashboard) + Plotly.js (UMAP) |
| Backend | FastAPI (async) |
| Orchestration | LangGraph |
| Embeddings | all-MiniLM-L6-v2 (sentence-transformers, local) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 (local) |
| Vector DB | PostgreSQL + pgvector (Supabase) |
| Keyword Search | BM25 (rank_bm25) |
| LLM | LLaMA 3.1 8B via Groq API |
| Deployment | Railway (backend) + Vercel (frontend) |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Supabase](https://supabase.com) account (free tier)
- A [Groq](https://console.groq.com) API key (free tier)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase and Groq credentials

# Run the pgvector schema on Supabase SQL Editor
# (paste the contents of scripts/schema.sql)

# Ingest data
python -m scripts.ingest

# Embed and store in pgvector
python -m scripts.embed_and_store

# Build BM25 index
python -m scripts.build_bm25

# Start the server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Ensure VITE_API_BASE_URL points to your backend

npm run dev
```

### Environment Variables

**Backend (`.env`):**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Supabase PostgreSQL connection string (asyncpg format) |
| `GROQ_API_KEY` | Groq API key for LLaMA 3.1 |
| `FRONTEND_URL` | Frontend URL for CORS |
| `CONFIDENCE_THRESHOLD` | Escalation threshold (default: 0.45) |

**Frontend (`.env`):**

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API URL |

## 📊 Evaluation Results

Evaluated on a hand-crafted test set of 30 support questions with ground truth answers.

| Metric | Score |
|--------|-------|
| Retrieval Recall@5 | _Run `python -m scripts.evaluate` to compute_ |
| ROUGE-L (response quality) | _Run evaluation_ |
| Citation Accuracy | _Run evaluation_ |
| Avg Confidence (correct answers) | _Run evaluation_ |

### Methodology

- **Recall@5**: Fraction of expected source chunks present in the top-5 reranked results
- **ROUGE-L**: Longest common subsequence overlap between generated and reference answers
- **Citation Accuracy**: Percentage of inline citations `[N]` that correctly reference a retrieved source

## 📁 Project Structure

```
saas-support-copilot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI endpoints
│   │   ├── config.py            # pydantic-settings
│   │   ├── ingestion/           # Data loading + chunking
│   │   ├── embeddings/          # Embedder + BM25
│   │   ├── retrieval/           # Router, semantic, BM25, RRF, reranker
│   │   ├── graph/               # LangGraph state + nodes + builder
│   │   ├── llm/                 # Groq async client
│   │   └── models/              # Pydantic schemas + DB connection
│   ├── scripts/                 # Ingestion, embedding, BM25, evaluation
│   ├── eval/                    # Test set + evaluation results
│   └── data/                    # Raw + processed data, BM25 index
├── frontend/
│   ├── src/
│   │   ├── pages/               # Home, Dashboard, Visualizer
│   │   ├── components/          # UI components
│   │   ├── hooks/               # useTicketSubmit
│   │   └── lib/                 # API client + utils
│   └── ...
└── docker-compose.yml
```

## 🔧 How It Works

1. **Ticket Submitted** → User types a support question
2. **Query Router** → Regex heuristics select relevant source types (docs, tickets, changelogs, errors)
3. **Hybrid Retrieval** → Semantic search (pgvector) + BM25 (in-memory) each return top 20 candidates
4. **Reciprocal Rank Fusion** → Merges results using rank-based fusion (k=60)
5. **Cross-Encoder Reranking** → Reranks fused candidates → top 5
6. **Confidence Scoring** → Sigmoid-normalized mean of top-3 reranker scores
7. **Escalation Check** → If confidence < 0.45, flag for human review
8. **LLM Generation** → LLaMA 3.1 generates cited response using top-5 context
9. **Response Display** → Draft response with clickable citations, confidence bar, sources panel

## 🎯 Design Decisions

- **RRF over weighted linear combination**: RRF only uses rank positions, not raw scores, so it works without cross-system score normalization
- **HNSW over IVFFlat**: HNSW requires no training step and provides better recall at our corpus size (<100K vectors)
- **Cross-encoder reranking**: Bi-encoder similarity is fast but imprecise; cross-encoder processes (query, passage) jointly for ~10-20% precision improvement
- **Sigmoid-normalized mean for confidence**: Using top-3 mean (not just top-1) penalizes queries with only one weak match, reducing false confidence

## 📈 Future Improvements

- [ ] Real-time ticket ingestion via webhooks
- [ ] User feedback loop (thumbs up/down) to fine-tune retrieval
- [ ] Multi-language support
- [ ] Streaming LLM responses via SSE
- [ ] Persistent conversation history in PostgreSQL
- [ ] A/B testing different retrieval strategies

## 📝 License

MIT
