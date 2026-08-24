"""Data loaders for all 4 source types.

- HuggingFace: MilaNLProc/customer-support-dialogues
- Public docs: loaded from cloned GitHub repos (Markdown files)
- Changelogs: loaded from local JSON files
- API errors: loaded from local JSON files
"""

import json
import glob
import os
from pathlib import Path
from typing import Optional

# Optional: only import datasets when actually downloading
try:
    from datasets import load_dataset
except ImportError:
    load_dataset = None


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def load_support_dialogues(output_dir: Optional[str] = None) -> list[dict]:
    """Download and process the HuggingFace customer-support-dialogues dataset.

    Each dialogue is flattened into a resolved ticket:
    customer question (first turn) + agent response (remaining turns).
    """
    if load_dataset is None:
        raise ImportError("Install 'datasets' package: pip install datasets")

    output_dir = output_dir or os.path.join(DATA_DIR, "raw", "support_dialogues")
    cache_path = os.path.join(output_dir, "tickets.json")

    # Use cache if available
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8-sig") as f:
            return json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    ds = load_dataset("MilaNLProc/customer-support-dialogues", split="train")

    processed = []
    for i, row in enumerate(ds):
        dialogue = row.get("dialogue", [])
        if len(dialogue) < 2:
            continue

        customer_query = dialogue[0]
        agent_response = " ".join(dialogue[1:])

        processed.append({
            "id": f"ticket_{i:05d}",
            "source_type": "resolved_ticket",
            "product": row.get("company", "unknown"),
            "customer_query": customer_query,
            "agent_response": agent_response,
            "full_text": f"Customer: {customer_query}\nAgent: {agent_response}",
            "timestamp": "2024-01-15",
        })

    with open(cache_path, "w") as f:
        json.dump(processed, f, indent=2)

    print(f"Processed {len(processed)} resolved tickets → {cache_path}")
    return processed


def load_markdown_docs(docs_dir: str, source_name: str) -> list[dict]:
    """Load all .md/.mdx files from a directory.

    Args:
        docs_dir: Path to directory containing Markdown files.
        source_name: Product name (e.g., 'vercel', 'supabase').

    Returns:
        List of document dicts with full_text and metadata.
    """
    docs = []
    patterns = ["**/*.md", "**/*.mdx"]

    for pattern in patterns:
        for fpath in glob.glob(os.path.join(docs_dir, pattern), recursive=True):
            try:
                text = Path(fpath).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            if len(text.strip()) < 100:  # Skip tiny files
                continue

            docs.append({
                "id": f"{source_name}_{Path(fpath).stem}",
                "source_type": "product_docs",
                "product": source_name,
                "file_path": fpath,
                "full_text": text,
                "timestamp": "2024-06-01",
            })

    print(f"Loaded {len(docs)} docs from {docs_dir}")
    return docs


def load_changelogs(changelogs_dir: Optional[str] = None) -> list[dict]:
    """Load changelog entries from JSON files in the changelogs directory.

    Each JSON file should contain a list of changelog entry dicts.
    """
    changelogs_dir = changelogs_dir or os.path.join(DATA_DIR, "changelogs")
    entries = []

    for fpath in glob.glob(os.path.join(changelogs_dir, "*.json")):
        with open(fpath, encoding="utf-8-sig") as f:
            data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)

    # Convert each entry to a document format
    docs = []
    for entry in entries:
        # Build a prose block from the structured entry
        text_parts = [
            f"# {entry.get('title', 'Untitled')}",
            f"Product: {entry.get('product', 'unknown')} | Version: {entry.get('version', 'N/A')} | Date: {entry.get('date', 'N/A')}",
            f"Category: {entry.get('category', 'N/A')}",
            "",
            entry.get("description", ""),
        ]

        breaking = entry.get("breaking_changes", [])
        if breaking:
            text_parts.append("\n## Breaking Changes")
            for bc in breaking:
                text_parts.append(f"- {bc}")

        migration = entry.get("migration_notes", "")
        if migration:
            text_parts.append(f"\n## Migration Notes\n{migration}")

        docs.append({
            "id": entry.get("id", f"cl_{len(docs):03d}"),
            "source_type": "changelog",
            "product": entry.get("product", "unknown"),
            "full_text": "\n".join(text_parts),
            "timestamp": entry.get("date", "2024-01-01"),
        })

    print(f"Loaded {len(docs)} changelog entries")
    return docs


def load_api_errors(errors_dir: Optional[str] = None) -> list[dict]:
    """Load API error reference entries from JSON files.

    Each JSON file should contain a list of error entry dicts.
    """
    errors_dir = errors_dir or os.path.join(DATA_DIR, "api_errors")
    entries = []

    for fpath in glob.glob(os.path.join(errors_dir, "*.json")):
        with open(fpath, encoding="utf-8-sig") as f:
            data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)

    docs = []
    for entry in entries:
        text_parts = [
            f"# Error: {entry.get('error_code', 'Unknown')} — {entry.get('message', '')}",
            f"Product: {entry.get('product', 'unknown')} | HTTP Status: {entry.get('http_status', 'N/A')}",
            "",
            entry.get("description", ""),
        ]

        causes = entry.get("common_causes", [])
        if causes:
            text_parts.append("\n## Common Causes")
            for cause in causes:
                text_parts.append(f"- {cause}")

        steps = entry.get("resolution_steps", [])
        if steps:
            text_parts.append("\n## Resolution Steps")
            for j, step in enumerate(steps, 1):
                text_parts.append(f"{j}. {step}")

        related = entry.get("related_docs", [])
        if related:
            text_parts.append("\n## Related Documentation")
            for doc in related:
                text_parts.append(f"- {doc}")

        docs.append({
            "id": entry.get("id", f"err_{len(docs):03d}"),
            "source_type": "api_error",
            "product": entry.get("product", "unknown"),
            "full_text": "\n".join(text_parts),
            "timestamp": "2024-06-01",
        })

    print(f"Loaded {len(docs)} API error references")
    return docs


def load_resolved_tickets_json(tickets_dir: Optional[str] = None) -> list[dict]:
    """Load resolved support tickets from JSON files.

    Each JSON file should contain a list of ticket dicts with
    ticket_id, product, question, resolution, etc.
    """
    tickets_dir = tickets_dir or os.path.join(DATA_DIR, "resolved_tickets")
    entries = []

    for fpath in glob.glob(os.path.join(tickets_dir, "*.json")):
        with open(fpath, encoding="utf-8-sig") as f:
            data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)

    docs = []
    for entry in entries:
        text_parts = [
            f"# Support Ticket: {entry.get('subject', 'Untitled')}",
            f"Product: {entry.get('product', 'unknown')} | Category: {entry.get('category', 'N/A')}",
            "",
            f"## Customer Issue",
            entry.get("question", ""),
            "",
            f"## Resolution",
            entry.get("resolution", ""),
        ]

        docs.append({
            "id": entry.get("ticket_id", f"tkt_{len(docs):03d}"),
            "source_type": "resolved_ticket",
            "product": entry.get("product", "unknown"),
            "full_text": "\n".join(text_parts),
            "timestamp": entry.get("timestamp", "2024-01-01"),
        })

    print(f"Loaded {len(docs)} resolved tickets from JSON")
    return docs


def load_product_docs_json(docs_dir: Optional[str] = None) -> list[dict]:
    """Load product documentation from JSON files.

    Scans data/product_docs/ for per-platform doc files
    (shopify_docs.json, stripe_docs.json, twilio_docs.json, vercel_docs.json).
    Each JSON file should contain a list of doc dicts with doc_id, product, title, content.
    """
    scan_dirs = [
        docs_dir or os.path.join(DATA_DIR, "product_docs"),
    ]
    entries = []

    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
        for fpath in glob.glob(os.path.join(scan_dir, "*.json")):
            with open(fpath, encoding="utf-8-sig") as f:
                data = json.load(f)
                if isinstance(data, list):
                    entries.extend(data)

    docs = []
    seen_ids = set()
    for entry in entries:
        doc_id = entry.get("doc_id", f"doc_{len(docs):03d}")
        if doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)

        # Support both 'content' (fetched from llms.txt) and older format
        text = entry.get("content", "") or entry.get("full_text", "")
        if len(text.strip()) < 100:
            continue

        docs.append({
            "id": doc_id,
            "source_type": "product_docs",
            "product": entry.get("product", "unknown"),
            "full_text": text,
            "timestamp": "2024-06-01",
        })

    print(f"Loaded {len(docs)} product docs from JSON (all sources)")
    return docs


