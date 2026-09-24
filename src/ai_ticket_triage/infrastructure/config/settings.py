"""Typed application settings boundary."""

from enum import StrEnum

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    """Supported runtime environments."""

    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "production"


class ProviderName(StrEnum):
    FAKE = "fake"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"


class Settings(BaseSettings):
    """Configuration loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Support Ticket Triage API"
    app_env: AppEnvironment = AppEnvironment.LOCAL
    database_url: str = "sqlite+aiosqlite:///./ai_ticket_triage.db"
    triage_provider: ProviderName = ProviderName.FAKE
    provider_model: str | None = None
    provider_timeout_seconds: float = 10.0
    provider_base_url: str | None = None
    provider_api_key: SecretStr | None = None
