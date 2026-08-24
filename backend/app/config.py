"""Application configuration via pydantic-settings.

Reads from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the SaaS Support Copilot backend."""

    # Database
    DATABASE_URL: str
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Groq LLM
    GROQ_API_KEY: str

    # Models
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Retrieval
    CONFIDENCE_THRESHOLD: float = 0.45
    MAX_RETRIEVAL_RESULTS: int = 20
    TOP_K_FINAL: int = 5

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # GitHub (for fetching real docs)
    GITHUB_TOKEN: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
