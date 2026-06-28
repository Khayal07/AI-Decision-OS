"""Runtime configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. Values come from the environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM provider — OpenRouter (OpenAI-compatible), free models.
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Model routing defaults (free OpenRouter model ids; override via env).
    model_judge: str = "openai/gpt-oss-120b:free"
    model_subagent: str = "openai/gpt-oss-20b:free"

    # Service auth (the Next.js BFF authenticates with this shared token).
    ai_service_token: str = "dev-internal-token"

    # CORS — only the BFF should call this service directly.
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
