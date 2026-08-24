"""Query router: determines which source types to search based on ticket content.

Uses regex-based heuristics for fast, zero-latency routing without LLM calls.
Always includes product_docs as a baseline. Falls back to all 4 sources if
no specific pattern matches.

Supports e-commerce platforms: Shopify, Stripe, Twilio, Vercel.
"""

import re

# Regex patterns that trigger specific source types
SOURCE_ROUTING_RULES: dict[str, list[str]] = {
    "api_error": [
        r"error\s*(code)?[\s:]*\d{3}",       # "error 401", "error code 500"
        r"status\s*code",
        r"exception|traceback|stack\s*trace",
        r"\b(4\d{2}|5\d{2})\b",               # HTTP status codes
        r"(jwt|token)\s*(expired|invalid)",
        r"permission\s*denied",
        r"rate\s*limit",
        r"timeout",
        r"card[_\s]declined",                  # Stripe-specific
        r"error\s*2\d{4}",                     # Twilio error codes (5 digits)
        r"webhook.*fail",                      # Webhook delivery failures
        r"FUNCTION_INVOCATION_TIMEOUT",        # Vercel-specific
        r"gateway[_\s]timeout",
    ],
    "changelog": [
        r"(latest|recent|new)\s*(update|change|release|version)",
        r"(deprecated|breaking\s*change|migration)",
        r"v\d+\.\d+",                          # Version numbers like v14.2.0
        r"what\s*(changed|is\s*new|was\s*updated)",
        r"(release\s*notes?|changelog)",
        r"(winter|spring|summer|fall)\s*\d{4}\s*edition",  # Shopify editions
    ],
    "resolved_ticket": [
        r"(same|similar)\s*(issue|problem|error)",
        r"(anyone|others)\s*(had|experienced|faced)",
        r"(how\s*did|how\s*to)\s*(fix|solve|resolve)",
        r"(workaround|known\s*issue)",
        r"not\s*(working|showing|loading|saving|delivering|arriving)",
        r"(can'?t|cannot|unable)\s*(add|create|send|deploy|connect|process)",
        r"customers?\s*(report|complain|say)",
    ],
}

# Product detection patterns for routing to specific platform docs
PRODUCT_PATTERNS: dict[str, list[str]] = {
    "shopify": [
        r"\bshopify\b", r"\bstore\b", r"\btheme\b", r"\bproduct\s*(listing|page)?\b",
        r"\border\b", r"\bshipping\b", r"\binventory\b", r"\bdiscount\s*code\b",
        r"\bcheckout\b.*\b(page|flow)\b", r"\bmerchant\b",
    ],
    "stripe": [
        r"\bstripe\b", r"\bpayment\b", r"\brefund\b", r"\bdispute\b",
        r"\bsubscription\b", r"\binvoice\b", r"\bpayout\b", r"\bcard\b",
        r"\bcharge\b", r"\bcheckout\s*session\b", r"\bwebhook\b",
    ],
    "twilio": [
        r"\btwilio\b", r"\bsms\b", r"\btext\s*message\b", r"\bverif(y|ication)\b",
        r"\bvoice\s*call\b", r"\bphone\s*number\b", r"\bnotification\b",
        r"\bmessaging\b", r"\b(2fa|two.factor)\b", r"\bwhatsapp\b",
    ],
    "vercel": [
        r"\bvercel\b", r"\bdeploy(ment)?\b", r"\bbuild\s*(fail|error|log)\b",
        r"\bserverless\b", r"\bedge\s*function\b", r"\bdomain\b",
        r"\benvironment\s*var", r"\bpreview\b", r"\bnext\.?js\b",
    ],
}

# Confidence threshold for escalation
CONFIDENCE_THRESHOLD = 0.45


def route_query(query: str) -> list[str]:
    """Determine which source types to search based on ticket content.

    Args:
        query: The support ticket text.

    Returns:
        List of source_type strings to search. Always includes 'product_docs'.
    """
    query_lower = query.lower()
    sources = {"product_docs"}  # Always search docs as baseline

    for source_type, patterns in SOURCE_ROUTING_RULES.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                sources.add(source_type)
                break

    # If no specific pattern fired, search all 4 sources
    # This ensures broad recall for ambiguous queries
    if sources == {"product_docs"}:
        sources = {"product_docs", "resolved_ticket", "changelog", "api_error"}

    return list(sources)


def detect_products(query: str) -> list[str]:
    """Detect which products a query is about.

    Args:
        query: The support ticket text.

    Returns:
        List of detected product names. Empty list if no specific product detected.
    """
    query_lower = query.lower()
    detected = []

    for product, patterns in PRODUCT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                detected.append(product)
                break

    return detected


def get_contact_for_query(query: str) -> str | None:
    """Get the primary product for contact routing.

    Returns the first detected product name, or None if ambiguous.
    """
    products = detect_products(query)
    return products[0] if products else None


def should_escalate(confidence: float, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
    """Determine if a ticket should be escalated to a human agent.

    Args:
        confidence: Float in [0, 1] from reranker confidence computation.
        threshold: Escalation threshold (default 0.45).

    Returns:
        True if the ticket should be escalated.
    """
    return confidence < threshold
