"""Async Groq API client for LLaMA 3.1 8B.

Uses the official groq Python SDK's AsyncGroq client for non-blocking
LLM calls. Includes retry logic for rate limiting (429).
"""

import asyncio
from groq import AsyncGroq, RateLimitError
from app.config import settings


# Initialize async Groq client
groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)

MODEL = "llama-3.1-8b-instant"


async def generate_completion(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 1024,
    max_retries: int = 3,
) -> str:
    """Generate a completion using Groq's LLaMA 3.1 8B.

    Args:
        prompt: The full prompt to send.
        temperature: Sampling temperature (0.3 for support = more deterministic).
        max_tokens: Maximum tokens in the response.
        max_retries: Number of retries on rate limiting.

    Returns:
        The generated text response.
    """
    for attempt in range(max_retries):
        try:
            response = await groq_client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except RateLimitError as e:
            retry_after = float(
                e.response.headers.get("retry-after", 2**attempt)
            )
            if attempt < max_retries - 1:
                print(f"Rate limited. Retrying in {retry_after}s (attempt {attempt + 1})")
                await asyncio.sleep(retry_after)
            else:
                return (
                    "[Rate Limited] The LLM service is temporarily unavailable. "
                    "Your ticket has been saved and will be processed shortly."
                )

        except Exception as e:
            return (
                f"[LLM Error] Unable to generate response: {str(e)}. "
                "Please try again or contact support."
            )
