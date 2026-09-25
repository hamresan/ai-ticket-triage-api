import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID

from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import Category, Priority, Sentiment
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
from tests.unit.infrastructure.providers.support.scripted_transport import (
    ScriptedChatCompletionTransport,
)


def test_openai_compatible_adapter_uses_shared_task_contract_and_mapping() -> None:
    async def exercise() -> None:
        transport = ScriptedChatCompletionTransport(
            json.dumps(
                {
                    "category": "billing",
                    "priority": "high",
                    "sentiment": "frustrated",
                    "needs_human_review": True,
                    "suggested_reply": "A billing specialist will review this charge.",
                }
            )
        )
        provider = OpenAICompatibleTriageProvider(
            model="compatible-model",
            transport=transport,
            prompt_builder=TriagePromptBuilder(),
            response_mapper=StructuredTriageResponseMapper(
                StructuredTriageOutputParser(StructuredTriageOutputValidator())
            ),
        )
        now = datetime(2026, 9, 25, tzinfo=UTC)
        ticket = Ticket(
            id=UUID("00000000-0000-0000-0000-000000000501"),
            subject=TicketSubject("Unexpected charge"),
            message=TicketMessage("I was charged twice and need help."),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )

        decision = await provider.triage(ticket)

        assert decision.category is Category.BILLING
        assert decision.priority is Priority.HIGH
        assert decision.sentiment is Sentiment.FRUSTRATED
        assert decision.needs_human_review is True
        assert len(transport.requests) == 1
        assert transport.requests[0].model == "compatible-model"
        assert "Unexpected charge" in transport.requests[0].prompt
        assert "I was charged twice and need help." in transport.requests[0].prompt

    asyncio.run(exercise())
