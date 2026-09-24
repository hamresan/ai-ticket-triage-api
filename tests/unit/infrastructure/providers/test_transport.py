import asyncio

import httpx
import pytest

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.transport import (
    ChatCompletionRequest,
    HttpxOllamaTransport,
)


def test_transport_returns_ollama_message_content() -> None:
    async def exercise() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/chat"
            return httpx.Response(
                200,
                json={"message": {"content": '{"category":"refund"}'}},
            )

        transport = HttpxOllamaTransport(
            base_url="http://ollama.test",
            timeout_seconds=1.0,
            http_transport=httpx.MockTransport(handler),
        )

        content = await transport.complete(ChatCompletionRequest("model", "prompt"))

        assert content == '{"category":"refund"}'

    asyncio.run(exercise())


@pytest.mark.parametrize("mode", ["timeout", "provider_error", "bad_json", "bad_envelope"])
def test_transport_maps_recoverable_failures(mode: str) -> None:
    async def exercise() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if mode == "timeout":
                raise httpx.ReadTimeout("timeout", request=request)
            if mode == "provider_error":
                return httpx.Response(503, request=request)
            if mode == "bad_json":
                return httpx.Response(200, content=b"not-json", request=request)
            return httpx.Response(200, json={"unexpected": True}, request=request)

        transport = HttpxOllamaTransport(
            base_url="http://ollama.test",
            timeout_seconds=1.0,
            http_transport=httpx.MockTransport(handler),
        )

        with pytest.raises(TriageProviderError):
            await transport.complete(ChatCompletionRequest("model", "prompt"))

    asyncio.run(exercise())
