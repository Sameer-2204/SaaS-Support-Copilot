"""Fetch e-commerce platform documentation from llms.txt endpoints.

Downloads curated documentation from Shopify, Stripe, Twilio, and Vercel
using their public llms.txt Markdown indices. Each platform's docs are
fetched as clean Markdown and saved as JSON for the ingestion pipeline.

Usage:
    python -m scripts.fetch_ecommerce_docs
    python -m scripts.fetch_ecommerce_docs --platform stripe
    python -m scripts.fetch_ecommerce_docs --max-per-platform 50
"""

import json
import os
import re
import sys
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ---------------------------------------------------------------------------
# Platform configurations
# ---------------------------------------------------------------------------
PLATFORMS = {
    "shopify": {
        "llms_txt_url": "https://shopify.dev/docs/llms.txt",
        "base_url": "https://shopify.dev",
        "fallback_urls": [
            "https://help.shopify.com/llms.txt",
        ],
        "max_articles": 100,
        "priority_keywords": [
            "getting-started", "store", "product", "order", "shipping",
            "payment", "checkout", "theme", "customer", "inventory",
            "discount", "refund", "tax", "domain", "app", "billing",
            "account", "login", "settings", "troubleshoot",
        ],
    },
    "stripe": {
        "llms_txt_url": "https://docs.stripe.com/llms.txt",
        "base_url": "https://docs.stripe.com",
        "max_articles": 100,
        "priority_keywords": [
            "checkout", "payment", "refund", "dispute", "subscription",
            "invoice", "customer", "webhook", "error", "testing",
            "connect", "payout", "currency", "card", "bank",
            "billing", "price", "product", "tax", "security",
        ],
    },
    "twilio": {
        "llms_txt_url": "https://www.twilio.com/docs/llms.txt",
        "base_url": "https://www.twilio.com",
        "max_articles": 80,
        "priority_keywords": [
            "sms", "messaging", "send", "receive", "phone", "number",
            "verify", "voice", "call", "notification", "alert",
            "whatsapp", "email", "sendgrid", "template", "webhook",
            "error", "troubleshoot", "pricing", "getting-started",
        ],
    },
    "vercel": {
        "llms_txt_url": "https://vercel.com/docs/llms.txt",
        "base_url": "https://vercel.com",
        "max_articles": 80,
        "priority_keywords": [
            "deploy", "build", "domain", "environment", "serverless",
            "function", "edge", "framework", "next", "error",
            "log", "preview", "production", "git", "team",
            "project", "analytics", "speed", "caching", "troubleshoot",
        ],
    },
}


def fetch_url(url: str, timeout: int = 15) -> str | None:
    """Fetch URL content as text with browser-like headers."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/plain, text/markdown, text/html, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  ✗ HTTP {e.code}: {url}")
        return None
    except Exception as e:
        print(f"  ✗ Error: {url} — {e}")
        return None


def parse_llms_txt(content: str, base_url: str) -> list[dict]:
    """Parse llms.txt Markdown to extract doc links with titles.

    Expected format:
        - [Title](https://example.com/path.md): Description
        or
        * [Title](/docs/path.md): Description
    """
    links = []
    # Match Markdown links: - [title](url) or * [title](url)
    pattern = r'[-*]\s*\[([^\]]+)\]\(([^)]+)\)(?:\s*:\s*(.+))?'

    for match in re.finditer(pattern, content):
        title = match.group(1).strip()
        url = match.group(2).strip()
        description = (match.group(3) or "").strip()

        # Normalize URL
        if url.startswith("/"):
            url = base_url.rstrip("/") + url
        elif not url.startswith("http"):
            url = base_url.rstrip("/") + "/" + url

        links.append({
            "title": title,
            "url": url,
            "description": description,
        })

    return links


def score_article(link: dict, priority_keywords: list[str]) -> int:
    """Score an article by relevance using keyword matching."""
    text = f"{link['title']} {link['description']} {link['url']}".lower()
    score = 0
    for keyword in priority_keywords:
        if keyword in text:
            score += 1
    return score


def select_articles(links: list[dict], platform_config: dict) -> list[dict]:
    """Select and prioritize articles up to the max limit."""
    max_articles = platform_config["max_articles"]
    keywords = platform_config["priority_keywords"]

    # Score and sort by relevance
    for link in links:
        link["_score"] = score_article(link, keywords)

    # Sort: high-scoring first, then alphabetically
    links.sort(key=lambda x: (-x["_score"], x["title"]))

    selected = links[:max_articles]
    for link in selected:
        del link["_score"]

    return selected


def fetch_article_content(url: str) -> str | None:
    """Fetch a single article's Markdown content.

    Tries the .md version first, then falls back to the HTML page.
    """
    # Try .md extension first (Stripe, Twilio serve Markdown directly)
    md_url = url
    if not md_url.endswith(".md"):
        # Some platforms serve .md versions at the same path
        md_url = url.rstrip("/") + ".md" if not url.endswith(".md") else url

    content = fetch_url(md_url)
    if content and len(content.strip()) > 200:
        # Clean up the Markdown
        return clean_markdown(content)

    # If .md didn't work, try the original URL
    if md_url != url:
        content = fetch_url(url)
        if content and len(content.strip()) > 200:
            return clean_markdown(content)

    return None


def clean_markdown(text: str) -> str:
    """Clean up fetched Markdown content."""
    # Remove HTML tags (keep content)
    text = re.sub(r'<[^>]+>', '', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    # Remove YAML frontmatter
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
    # Truncate very long docs (will be chunked anyway)
    if len(text) > 5000:
        text = text[:5000]
    return text.strip()


def fetch_platform_docs(platform: str, config: dict) -> list[dict]:
    """Fetch all docs for a single platform."""
    print(f"\n{'='*60}")
    print(f"  Fetching {platform.upper()} docs")
    print(f"{'='*60}")

    # Step 1: Fetch llms.txt index (try primary, then fallbacks)
    print(f"  Fetching llms.txt from {config['llms_txt_url']}...")
    index_content = fetch_url(config["llms_txt_url"], timeout=30)

    if not index_content and "fallback_urls" in config:
        for fallback in config["fallback_urls"]:
            print(f"  Trying fallback: {fallback}...")
            index_content = fetch_url(fallback, timeout=30)
            if index_content:
                break

    if not index_content:
        print(f"  ✗ Failed to fetch llms.txt for {platform} (all URLs failed)")
        return []

    # Step 2: Parse links
    links = parse_llms_txt(index_content, config["base_url"])
    print(f"  Found {len(links)} doc links in llms.txt")

    if not links:
        print(f"  ✗ No links found in llms.txt for {platform}")
        return []

    # Step 3: Select top articles
    selected = select_articles(links, config)
    print(f"  Selected {len(selected)} articles (max: {config['max_articles']})")

    # Step 4: Fetch each article's content
    docs = []
    failed = 0
    for i, link in enumerate(selected):
        content = fetch_article_content(link["url"])
        if not content or len(content.strip()) < 150:
            failed += 1
            continue

        doc = {
            "doc_id": f"{platform}_{i:04d}",
            "product": platform,
            "category": categorize_doc(link["title"], link["url"]),
            "title": link["title"],
            "content": content,
        }
        docs.append(doc)

        if (i + 1) % 20 == 0:
            print(f"    → {i + 1}/{len(selected)} fetched ({len(docs)} valid, {failed} skipped)")

        time.sleep(0.15)  # Rate-limit: ~6 req/sec

    print(f"  ✅ {len(docs)} articles fetched ({failed} skipped)")
    return docs


def categorize_doc(title: str, url: str) -> str:
    """Auto-categorize a doc based on title/URL keywords."""
    text = f"{title} {url}".lower()

    categories = {
        "getting-started": ["getting-started", "quickstart", "setup", "install", "introduction", "overview"],
        "billing": ["billing", "pricing", "invoice", "subscription", "plan", "cost", "charge"],
        "authentication": ["auth", "login", "signup", "password", "sso", "oauth", "session", "jwt", "token"],
        "troubleshooting": ["troubleshoot", "error", "debug", "fix", "issue", "problem", "fail"],
        "api-reference": ["api", "endpoint", "reference", "sdk", "library", "client"],
        "deployment": ["deploy", "build", "ci", "cd", "release", "production", "staging"],
        "database": ["database", "query", "table", "migration", "schema", "sql", "postgres"],
        "integration": ["integration", "webhook", "connect", "plugin", "extension", "app"],
        "security": ["security", "permission", "role", "policy", "encryption", "compliance"],
        "configuration": ["config", "setting", "environment", "variable", "domain", "dns"],
    }

    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                return category

    return "general"


def save_docs(platform: str, docs: list[dict]):
    """Save fetched docs to the data directory."""
    out_dir = os.path.join(DATA_DIR, "product_docs")
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, f"{platform}_docs.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"  💾 Saved {len(docs)} docs → {out_path} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Fetch e-commerce platform docs from llms.txt")
    parser.add_argument(
        "--platform",
        choices=list(PLATFORMS.keys()) + ["all"],
        default="all",
        help="Which platform to fetch (default: all)",
    )
    parser.add_argument(
        "--max-per-platform",
        type=int,
        default=None,
        help="Override max articles per platform",
    )
    args = parser.parse_args()

    platforms = list(PLATFORMS.keys()) if args.platform == "all" else [args.platform]

    # Override max if specified
    if args.max_per_platform:
        for p in platforms:
            PLATFORMS[p]["max_articles"] = args.max_per_platform

    total_docs = 0
    for platform in platforms:
        config = PLATFORMS[platform]
        docs = fetch_platform_docs(platform, config)
        if docs:
            save_docs(platform, docs)
            total_docs += len(docs)

    # Also remove old data files
    old_files = [
        os.path.join(DATA_DIR, "product_docs", "docs.json"),
        os.path.join(DATA_DIR, "raw", "supabase_docs", "docs.json"),
    ]
    for old_file in old_files:
        if os.path.exists(old_file):
            os.remove(old_file)
            print(f"  🗑️  Removed old file: {old_file}")

    print(f"\n{'='*60}")
    print(f"  ✅ Done. Fetched {total_docs} total docs across {len(platforms)} platforms.")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("  1. Run: python -m scripts.generate_synthetic_data")
    print("  2. Run: python -m scripts.ingest")
    print("  3. Run: python -m scripts.embed_and_store")
    print("  4. Run: python -m scripts.build_bm25")


if __name__ == "__main__":
    main()
