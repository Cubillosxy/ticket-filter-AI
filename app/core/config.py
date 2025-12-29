from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ticket-classifier"
    environment: str = "local"

    # AI
    ai_provider: str = "none"  # "openai" | "none"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    ai_timeout_ms: int = 2000

    # Persistence
    audit_db_path: str = "./data/audit.db"

    # Guardrails (future-ready flags)
    enable_pii_redaction: bool = False
    enable_async_reprocess: bool = False


settings = Settings()
