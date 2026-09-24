from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.infrastructure.config.settings import ProviderName, Settings
from ai_ticket_triage.infrastructure.providers.fake import FakeTriageProvider
from ai_ticket_triage.infrastructure.providers.ollama import OllamaTriageProvider
from ai_ticket_triage.infrastructure.providers.openai_compatible import (
    OpenAICompatibleTriageProvider,
)
from ai_ticket_triage.infrastructure.providers.structured import (
    StructuredTriageResponseMapper,
    TriagePromptBuilder,
)
from ai_ticket_triage.infrastructure.providers.structured.parser import StructuredTriageOutputParser
from ai_ticket_triage.infrastructure.providers.structured.validator import (
    StructuredTriageOutputValidator,
)
from ai_ticket_triage.infrastructure.providers.transport import (
    HttpxOllamaTransport,
    HttpxOpenAICompatibleTransport,
)


class ProviderConfigurationError(ValueError):
    pass


class TriageProviderFactory:
    def create(self, settings: Settings) -> TriageProvider:
        if settings.triage_provider is ProviderName.FAKE:
            return FakeTriageProvider()
        if settings.triage_provider is ProviderName.OLLAMA:
            if not settings.provider_model:
                raise ProviderConfigurationError("PROVIDER_MODEL is required for Ollama.")
            if not settings.provider_base_url:
                raise ProviderConfigurationError("PROVIDER_BASE_URL is required for Ollama.")
            return OllamaTriageProvider(
                model=settings.provider_model,
                transport=HttpxOllamaTransport(
                    base_url=settings.provider_base_url,
                    timeout_seconds=settings.provider_timeout_seconds,
                ),
                prompt_builder=TriagePromptBuilder(),
                response_mapper=StructuredTriageResponseMapper(
                    StructuredTriageOutputParser(StructuredTriageOutputValidator())
                ),
            )
        if settings.triage_provider is ProviderName.OPENAI_COMPATIBLE:
            if not settings.provider_model:
                raise ProviderConfigurationError(
                    "PROVIDER_MODEL is required for OpenAI-compatible providers."
                )
            if not settings.provider_base_url:
                raise ProviderConfigurationError(
                    "PROVIDER_BASE_URL is required for OpenAI-compatible providers."
                )
            api_key = (
                settings.provider_api_key.get_secret_value()
                if settings.provider_api_key is not None
                else None
            )
            return OpenAICompatibleTriageProvider(
                model=settings.provider_model,
                transport=HttpxOpenAICompatibleTransport(
                    base_url=settings.provider_base_url,
                    timeout_seconds=settings.provider_timeout_seconds,
                    api_key=api_key,
                ),
                prompt_builder=TriagePromptBuilder(),
                response_mapper=StructuredTriageResponseMapper(
                    StructuredTriageOutputParser(StructuredTriageOutputValidator())
                ),
            )
        raise ProviderConfigurationError(
            f"Unsupported triage provider: {settings.triage_provider!s}"
        )
