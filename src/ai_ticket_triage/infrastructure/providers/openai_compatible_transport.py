import httpx

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.transport import (
    ChatCompletionRequest,
    ChatCompletionTransport,
)


class HttpxOpenAICompatibleTransport(ChatCompletionTransport):
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float,
        api_key: str | None = None,
        http_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._api_key = api_key
        self._http_transport = http_transport

    async def complete(self, request: ChatCompletionRequest) -> str:
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else None
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds,
                transport=self._http_transport,
            ) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                body = response.json()
        except (httpx.TimeoutException, httpx.HTTPError, ValueError) as exc:
            raise TriageProviderError("OpenAI-compatible request failed.") from exc
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise TriageProviderError(
                "OpenAI-compatible provider returned an invalid response envelope."
            ) from exc
        if not isinstance(content, str):
            raise TriageProviderError(
                "OpenAI-compatible provider returned an invalid response content type."
            )
        return content
