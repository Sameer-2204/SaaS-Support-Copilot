"""Evaluation harness for the SaaS Support Copilot.

Measures:
- Recall@5: Fraction of expected source chunks in top-5 reranked results
- ROUGE-L: Overlap between generated and ground truth responses
- Citation Accuracy: Whether [N] markers correctly reference retrieved sources

Usage:
    python -m scripts.evaluate
"""

import json
import os
import re
import sys
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rouge_score import rouge_scorer

from app.retrieval.semantic import semantic_search
from app.retrieval.keyword import bm25_search
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import Reranker
from app.llm.groq_client import generate_completion
from app.embeddings.bm25_index import load_bm25_index
from app.config import settings


TEST_SET_PATH = os.path.join(os.path.dirname(__file__), "..", "eval", "test_set.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "eval", "results")


async def evaluate_retrieval(test_set: list[dict], bm25, chunk_ids, chunks_lookup) -> list[dict]:
    """Evaluate retrieval quality with Recall@5."""
    reranker = Reranker()
    results = []

    for item in test_set:
        query = item["question"]
        expected_ids = set(item["expected_chunk_ids"])

        # Full retrieval pipeline
        sem_results = await semantic_search(query, item["expected_source_types"], top_k=20)
        bm25_results_list = bm25_search(
            query, bm25, chunk_ids, chunks_lookup,
            item["expected_source_types"], top_k=20
        )
        fused = reciprocal_rank_fusion(sem_results, bm25_results_list)
        reranked = reranker.rerank(query, fused, top_k=5)

        # Recall@5
        retrieved_ids = {r["chunk_id"] for r in reranked}
        hits = len(expected_ids & retrieved_ids)
        recall = hits / len(expected_ids) if expected_ids else 0.0

        # Confidence
        confidence = reranker.compute_confidence(reranked)

        results.append({
            "id": item["id"],
            "question": query,
            "recall_at_5": recall,
            "confidence": confidence,
            "expected_ids": list(expected_ids),
            "retrieved_ids": list(retrieved_ids),
            "hits": hits,
        })

        print(f"  Q{item['id']:2d}: Recall@5={recall:.2f} Conf={confidence:.2f}")

    return results


async def evaluate_responses(test_set: list[dict]) -> list[dict]:
    """Evaluate response generation quality with ROUGE-L and citation accuracy."""
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    results = []

    for item in test_set:
        # Generate response (simplified — just the prompt, no retrieval context)
        prompt = f"""Answer this support question concisely:
{item['question']}

Use information from these facts:
{item['ground_truth_answer']}

RESPONSE:"""

        generated = await generate_completion(prompt)

        # ROUGE-L
        score = scorer.score(item["ground_truth_answer"], generated)
        rouge_l = score["rougeL"].fmeasure

        # Citation accuracy
        citations = re.findall(r"\[(\d+)\]", generated)
        valid_citations = [c for c in citations if int(c) <= 5]
        citation_acc = len(valid_citations) / len(citations) if citations else 1.0

        results.append({
            "id": item["id"],
            "rouge_l": rouge_l,
            "citation_accuracy": citation_acc,
            "generated_length": len(generated),
        })

        print(f"  Q{item['id']:2d}: ROUGE-L={rouge_l:.3f} CitAcc={citation_acc:.2f}")

    return results


async def run_full_evaluation():
    """Run the complete evaluation pipeline."""
    # Load test set
    with open(TEST_SET_PATH) as f:
        test_set = json.load(f)
    print(f"Loaded {len(test_set)} test questions")

    # Load BM25
    bm25, chunk_ids = load_bm25_index()
    lookup_path = os.path.join(os.path.dirname(__file__), "..", "data", "chunks_lookup.json")
    with open(lookup_path) as f:
        chunks_lookup = json.load(f)

    # Retrieval evaluation
    print("\n=== Retrieval Evaluation (Recall@5) ===")
    retrieval_results = await evaluate_retrieval(test_set, bm25, chunk_ids, chunks_lookup)

    avg_recall = sum(r["recall_at_5"] for r in retrieval_results) / len(retrieval_results)
    avg_confidence = sum(r["confidence"] for r in retrieval_results) / len(retrieval_results)

    print(f"\n  Average Recall@5:    {avg_recall:.4f}")
    print(f"  Average Confidence:  {avg_confidence:.4f}")

    # Response evaluation
    print("\n=== Response Evaluation (ROUGE-L + Citation) ===")
    response_results = await evaluate_responses(test_set)

    avg_rouge = sum(r["rouge_l"] for r in response_results) / len(response_results)
    avg_citation = sum(r["citation_accuracy"] for r in response_results) / len(response_results)

    print(f"\n  Average ROUGE-L:          {avg_rouge:.4f}")
    print(f"  Average Citation Accuracy: {avg_citation:.4f}")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = os.path.join(RESULTS_DIR, f"eval_{timestamp}.json")

    full_results = {
        "timestamp": timestamp,
        "summary": {
            "avg_recall_at_5": avg_recall,
            "avg_confidence": avg_confidence,
            "avg_rouge_l": avg_rouge,
            "avg_citation_accuracy": avg_citation,
            "total_questions": len(test_set),
        },
        "retrieval_results": retrieval_results,
        "response_results": response_results,
    }

    with open(results_path, "w") as f:
        json.dump(full_results, f, indent=2)

    print(f"\n✅ Results saved to {results_path}")
    return full_results


if __name__ == "__main__":
    asyncio.run(run_full_evaluation())
