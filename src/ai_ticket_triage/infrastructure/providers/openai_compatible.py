from dataclasses import dataclass

from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import TriageDecision
from ai_ticket_triage.infrastructure.providers.structured import (
    StructuredTriageResponseMapper,
    TriagePromptBuilder,
    TriageTaskInputV1,
)
from ai_ticket_triage.infrastructure.providers.transport import (
    ChatCompletionRequest,
    ChatCompletionTransport,
)


@dataclass(frozen=True, slots=True)
class OpenAICompatibleTriageProvider(TriageProvider):
    model: str
    transport: ChatCompletionTransport
    prompt_builder: TriagePromptBuilder
    response_mapper: StructuredTriageResponseMapper

    async def triage(self, ticket: Ticket) -> TriageDecision:
        prompt = self.prompt_builder.build(
            TriageTaskInputV1(
                subject=ticket.subject.value,
                message=ticket.message.value,
            )
        )
        content = await self.transport.complete(ChatCompletionRequest(self.model, prompt))
        return self.response_mapper.map(content)
