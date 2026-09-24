from dataclasses import dataclass
from typing import Protocol

import httpx

from ai_ticket_triage.application.triage.errors import TriageProviderError


@dataclass(frozen=True, slots=True)
class ChatCompletionRequest:
    model: str
    prompt: str


class ChatCompletionTransport(Protocol):
    async def complete(self, request: ChatCompletionRequest) -> str: ...


class HttpxOllamaTransport(ChatCompletionTransport):
    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def complete(self, request: ChatCompletionRequest) -> str:
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "stream": False,
            "format": "json",
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
                body = response.json()
        except (httpx.TimeoutException, httpx.HTTPError, ValueError) as exc:
            raise TriageProviderError("Ollama request failed.") from exc
        try:
            content = body["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise TriageProviderError("Ollama returned an invalid response envelope.") from exc
        if not isinstance(content, str):
            raise TriageProviderError("Ollama returned an invalid response content type.")
        return content
