from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.transport import (
    ChatCompletionRequest,
    ChatCompletionTransport,
)


class ScriptedChatCompletionTransport(ChatCompletionTransport):
    def __init__(self, content: str) -> None:
        self.content = content
        self.requests: list[ChatCompletionRequest] = []

    async def complete(self, request: ChatCompletionRequest) -> str:
        self.requests.append(request)
        return self.content


class FailingChatCompletionTransport(ChatCompletionTransport):
    async def complete(self, request: ChatCompletionRequest) -> str:
        raise TriageProviderError("Scripted provider failure.")
