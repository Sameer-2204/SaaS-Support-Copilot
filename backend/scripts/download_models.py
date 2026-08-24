"""Pre-export both ML models to ONNX format at Docker build time.

Run once during image build so the container starts with ONNX files
already on disk — no export delay on the first request.
"""
import os

SENTENCE_TRANSFORMERS_HOME = os.environ.get(
    "SENTENCE_TRANSFORMERS_HOME", "/app/models_cache"
)

# ── Embedder ──────────────────────────────────────────────────────────────────
print("Exporting embedder to ONNX...")
from sentence_transformers import SentenceTransformer  # noqa: E402

SentenceTransformer("all-MiniLM-L6-v2", backend="onnx")
print("Embedder ONNX export done")

# ── Cross-encoder reranker ────────────────────────────────────────────────────
print("Exporting cross-encoder to ONNX...")
from optimum.onnxruntime import ORTModelForSequenceClassification  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

cache_dir = os.path.join(SENTENCE_TRANSFORMERS_HOME, "cross-encoder-onnx")
os.makedirs(cache_dir, exist_ok=True)

model = ORTModelForSequenceClassification.from_pretrained(
    "cross-encoder/ms-marco-MiniLM-L-6-v2", export=True
)
model.save_pretrained(cache_dir)

AutoTokenizer.from_pretrained(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
).save_pretrained(cache_dir)

print(f"Cross-encoder ONNX saved to {cache_dir}")
print("All models exported successfully")
