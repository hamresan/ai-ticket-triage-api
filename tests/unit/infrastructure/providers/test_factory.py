import pytest

from ai_ticket_triage.infrastructure.config import ProviderName, Settings
from ai_ticket_triage.infrastructure.providers import (
    FakeTriageProvider,
    OllamaTriageProvider,
    ProviderConfigurationError,
    TriageProviderFactory,
)


def test_factory_builds_fake_provider_by_default() -> None:
    provider = TriageProviderFactory().create(Settings())

    assert isinstance(provider, FakeTriageProvider)


def test_factory_builds_ollama_from_typed_settings() -> None:
    settings = Settings(
        triage_provider=ProviderName.OLLAMA,
        provider_model="llama-test",
        provider_base_url="http://localhost:11434",
        provider_timeout_seconds=2.5,
    )

    provider = TriageProviderFactory().create(settings)

    assert isinstance(provider, OllamaTriageProvider)
    assert provider.model == "llama-test"


@pytest.mark.parametrize(
    ("model", "base_url"),
    [(None, "http://localhost:11434"), ("llama-test", None)],
)
def test_factory_rejects_missing_ollama_configuration(
    model: str | None, base_url: str | None
) -> None:
    settings = Settings(
        triage_provider=ProviderName.OLLAMA,
        provider_model=model,
        provider_base_url=base_url,
    )

    with pytest.raises(ProviderConfigurationError):
        TriageProviderFactory().create(settings)
