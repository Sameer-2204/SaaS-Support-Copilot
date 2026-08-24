#!/usr/bin/env bash
# Render build script — runs once at deploy time (not on every request)
# Installs deps, pre-downloads model weights, and builds BM25 index.

set -e  # Exit on any error

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

echo "=== Pre-downloading model weights ==="
python -c "
from sentence_transformers import SentenceTransformer
import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = './models_cache'
SentenceTransformer('all-MiniLM-L6-v2')
SentenceTransformer('cross-encoder/ms-marco-MiniLM-L-6-v2')
print('Models downloaded successfully')
"

echo "=== Running ingestion pipeline ==="
python -m scripts.ingest

echo "=== Building BM25 index ==="
python -m scripts.build_bm25

echo "=== Build complete ==="
