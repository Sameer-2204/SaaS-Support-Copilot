"""Fetch real Supabase and Vercel documentation from their public GitHub repos.

Uses the GitHub Contents API to list files, then fetches raw markdown content.
Works without authentication (60 req/hr) or with a PAT (5000 req/hr).

Usage:
    python -m scripts.fetch_real_docs
    python -m scripts.fetch_real_docs --token ghp_your_token_here
    python -m scripts.fetch_real_docs --product supabase
    python -m scripts.fetch_real_docs --product vercel
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Configuration: which paths to fetch from each repo
# ---------------------------------------------------------------------------
SOURCES = {
    "supabase": {
        "repo": "supabase/supabase",
        "paths": [
            "apps/docs/content/guides/auth",
            "apps/docs/content/guides/database",
            "apps/docs/content/guides/storage",
            "apps/docs/content/guides/realtime",
            "apps/docs/content/guides/functions",
            "apps/docs/content/guides/api",
            "apps/docs/content/guides/getting-started",
            "apps/docs/content/guides/platform",
            "apps/docs/content/reference/javascript",
        ],
        "branch": "master",
        "max_files": 200,
    },
    "vercel": {
        "repo": "vercel/next.js",
        "paths": [
            "docs/01-app",
            "docs/02-pages",
            "docs/03-architecture",
            "docs/04-community",
        ],
        "branch": "canary",
        "max_files": 150,
    },
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"


def make_request(url: str, token: str | None = None) -> dict | list | None:
    """Make a GitHub API request with optional auth."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "SaaS-Support-Copilot-RAG/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            remaining = resp.headers.get("X-RateLimit-Remaining", "?")
            if remaining != "?" and int(remaining) < 5:
                print(f"  ⚠ Rate limit low ({remaining} remaining). Sleeping 60s...")
                time.sleep(60)
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  ✗ Rate limited on {url}. Pass --token to increase limits.")
        elif e.code == 404:
            print(f"  ✗ Not found: {url}")
        else:
            print(f"  ✗ HTTP {e.code} on {url}")
        return None
    except Exception as e:
        print(f"  ✗ Error fetching {url}: {e}")
        return None


def fetch_raw_content(repo: str, branch: str, filepath: str, token: str | None = None) -> str | None:
    """Fetch raw file content from GitHub."""
    url = f"{GITHUB_RAW}/{repo}/{branch}/{filepath}"
    headers = {"User-Agent": "SaaS-Support-Copilot-RAG/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def list_directory(repo: str, path: str, branch: str, token: str | None = None) -> list[dict]:
    """List files in a GitHub repo directory recursively."""
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}?ref={branch}"
    items = make_request(url, token)
    if not items or not isinstance(items, list):
        return []

    files = []
    for item in items:
        if item["type"] == "file" and item["name"].endswith((".md", ".mdx")):
            files.append(item)
        elif item["type"] == "dir":
            # Recurse one level
            sub_items = make_request(item["url"], token)
            if sub_items and isinstance(sub_items, list):
                for sub in sub_items:
                    if sub["type"] == "file" and sub["name"].endswith((".md", ".mdx")):
                        files.append(sub)
    return files


def fetch_product_docs(product: str, config: dict, token: str | None = None) -> list[dict]:
    """Fetch all docs for a product and return as document dicts."""
    repo = config["repo"]
    branch = config["branch"]
    max_files = config["max_files"]
    out_dir = os.path.join(DATA_DIR, f"{product}_docs")
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n=== Fetching {product.upper()} docs from {repo} ===")

    # Collect all file listings
    all_files = []
    for path in config["paths"]:
        print(f"  Listing {path}...")
        files = list_directory(repo, path, branch, token)
        all_files.extend(files)
        time.sleep(0.3)  # Be polite
        if len(all_files) >= max_files:
            break

    all_files = all_files[:max_files]
    print(f"  Found {len(all_files)} markdown files. Fetching content...")

    docs = []
    for i, file_info in enumerate(all_files):
        filepath = file_info["path"]
        name = Path(filepath).stem

        # Skip tiny files and index/nav files
        if file_info.get("size", 999) < 200:
            continue
        if name in ("index", "nav", "_meta", "sidebar", "toc"):
            continue

        content = fetch_raw_content(repo, branch, filepath, token)
        if not content or len(content.strip()) < 150:
            continue

        # Truncate very long files to ~3000 chars (will be chunked anyway)
        content = content[:4000] if len(content) > 4000 else content

        doc = {
            "doc_id": f"{product}_{name}_{i:04d}",
            "product": product,
            "source_type": "product_docs",
            "title": name.replace("-", " ").replace("_", " ").title(),
            "filepath": filepath,
            "content": content,
        }
        docs.append(doc)

        if (i + 1) % 20 == 0:
            print(f"    → {i + 1}/{len(all_files)} files fetched ({len(docs)} valid)")

        time.sleep(0.1)  # Rate-limit buffer for raw.githubusercontent.com

    # Save to file
    out_path = os.path.join(out_dir, "docs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Saved {len(docs)} {product} docs → {out_path}")
    return docs


def main():
    parser = argparse.ArgumentParser(description="Fetch real docs from GitHub")
    parser.add_argument("--token", default=None, help="GitHub Personal Access Token")
    parser.add_argument(
        "--product",
        choices=["supabase", "vercel", "both"],
        default="both",
        help="Which product to fetch (default: both)",
    )
    args = parser.parse_args()

    # Also check .env for GITHUB_TOKEN
    token = args.token
    if not token:
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN="):
                        token = line.strip().split("=", 1)[1]
                        break

    if token:
        print(f"✅ Using GitHub token (5000 req/hr limit)")
    else:
        print("⚠ No GitHub token — using unauthenticated requests (60 req/hr).")
        print("  Pass --token ghp_xxx or add GITHUB_TOKEN=ghp_xxx to .env for faster fetching.")

    products = (
        ["supabase", "vercel"] if args.product == "both" else [args.product]
    )

    total_docs = 0
    for product in products:
        if product in SOURCES:
            docs = fetch_product_docs(product, SOURCES[product], token)
            total_docs += len(docs)

    print(f"\n✅ Done. Fetched {total_docs} total documentation pages.")
    print("\nNext steps:")
    print("  1. Run: python -m scripts.ingest")
    print("  2. Run: python -m scripts.embed_and_store")
    print("  3. Run: python -m scripts.build_bm25")


if __name__ == "__main__":
    main()
