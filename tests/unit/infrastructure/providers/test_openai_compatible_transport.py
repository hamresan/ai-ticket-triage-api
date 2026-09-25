import asyncio
import json

import httpx
import pytest

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.openai_compatible_transport import (
    HttpxOpenAICompatibleTransport,
)
from ai_ticket_triage.infrastructure.providers.transport import ChatCompletionRequest


def test_transport_maps_openai_compatible_request_and_response() -> None:
    async def exercise() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/chat/completions"
            assert request.headers["authorization"] == "Bearer test-key"
            payload = json.loads(request.content)
            assert payload == {
                "model": "test-model",
                "messages": [{"role": "user", "content": "test prompt"}],
            }
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": '{"category":"technical"}'}}]},
            )

        transport = HttpxOpenAICompatibleTransport(
            base_url="https://provider.test/v1",
            timeout_seconds=1.0,
            api_key="test-key",
            http_transport=httpx.MockTransport(handler),
        )

        content = await transport.complete(ChatCompletionRequest("test-model", "test prompt"))

        assert content == '{"category":"technical"}'

    asyncio.run(exercise())


def test_transport_omits_auth_when_key_is_not_configured() -> None:
    async def exercise() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "authorization" not in request.headers
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "{}"}}]},
            )

        transport = HttpxOpenAICompatibleTransport(
            base_url="http://local-compatible.test/v1",
            timeout_seconds=1.0,
            http_transport=httpx.MockTransport(handler),
        )

        assert await transport.complete(ChatCompletionRequest("model", "prompt")) == "{}"

    asyncio.run(exercise())


@pytest.mark.parametrize(
    "mode",
    ["timeout", "provider_error", "bad_json", "empty_choices", "bad_envelope", "bad_content"],
)
def test_transport_maps_recoverable_failures(mode: str) -> None:
    async def exercise() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if mode == "timeout":
                raise httpx.ReadTimeout("timeout", request=request)
            if mode == "provider_error":
                return httpx.Response(503, request=request)
            if mode == "bad_json":
                return httpx.Response(200, content=b"not-json", request=request)
            if mode == "empty_choices":
                return httpx.Response(200, json={"choices": []}, request=request)
            if mode == "bad_envelope":
                return httpx.Response(200, json={"unexpected": True}, request=request)
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": {"text": "invalid"}}}]},
                request=request,
            )

        transport = HttpxOpenAICompatibleTransport(
            base_url="https://provider.test/v1",
            timeout_seconds=1.0,
            http_transport=httpx.MockTransport(handler),
        )

        with pytest.raises(TriageProviderError):
            await transport.complete(ChatCompletionRequest("model", "prompt"))

    asyncio.run(exercise())
