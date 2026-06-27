"""Runtime configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. Values come from the environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM providers
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    voyage_api_key: str = ""

    # Model routing defaults (see plan §11 — Model Router)
    model_judge: str = "claude-opus-4-8"
    model_subagent: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "voyage-3"

    # Service auth (the Next.js BFF authenticates with this shared token)
    ai_service_token: str = "dev-internal-token"

    # CORS — only the BFF should call this service directly
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
