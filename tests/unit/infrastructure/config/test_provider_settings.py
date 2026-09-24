import pytest
from pydantic import SecretStr, ValidationError

from ai_ticket_triage.infrastructure.config import ProviderName, Settings


def test_provider_settings_are_typed() -> None:
    settings = Settings(
        triage_provider=ProviderName.OLLAMA,
        provider_model="model",
        provider_timeout_seconds=3.0,
        provider_base_url="http://localhost:11434",
        provider_api_key=SecretStr("secret-placeholder"),
    )

    assert settings.triage_provider is ProviderName.OLLAMA
    assert settings.provider_timeout_seconds == 3.0
    assert settings.provider_api_key is not None
    assert str(settings.provider_api_key) == "**********"


def test_unsupported_provider_configuration_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"triage_provider": "unsupported"})
