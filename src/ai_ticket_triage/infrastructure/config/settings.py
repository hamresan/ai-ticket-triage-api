"""Typed application settings boundary."""

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    """Supported runtime environments."""

    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Configuration loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Support Ticket Triage API"
    app_env: AppEnvironment = AppEnvironment.LOCAL
