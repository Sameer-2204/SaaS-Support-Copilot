FROM python:3.11-slim

WORKDIR /app

# Install system deps for building native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Install torch CPU-only first (separate layer for caching)
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY . .

# Pre-export both models to ONNX at build time (baked into image, no torch at inference)
ENV SENTENCE_TRANSFORMERS_HOME=/app/models_cache
RUN python scripts/download_models.py

# Build BM25 index from source data (no DB needed for this step)
RUN python -m scripts.ingest && python -m scripts.build_bm25

# Hugging Face Spaces runs as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use shell form so $PORT env var works on both HF Spaces and Railway
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
