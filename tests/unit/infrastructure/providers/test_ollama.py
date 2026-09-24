import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID

from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import Category
from ai_ticket_triage.infrastructure.providers.ollama import OllamaTriageProvider
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


def test_ollama_adapter_maps_ticket_request_and_structured_response() -> None:
    async def exercise() -> None:
        transport = ScriptedChatCompletionTransport(
            json.dumps(
                {
                    "category": "technical",
                    "priority": "medium",
                    "sentiment": "negative",
                    "needs_human_review": False,
                    "suggested_reply": "Please try the troubleshooting steps.",
                }
            )
        )
        provider = OllamaTriageProvider(
            model="test-model",
            transport=transport,
            prompt_builder=TriagePromptBuilder(),
            response_mapper=StructuredTriageResponseMapper(
                StructuredTriageOutputParser(StructuredTriageOutputValidator())
            ),
        )
        now = datetime(2026, 9, 24, tzinfo=UTC)
        ticket = Ticket(
            id=UUID("00000000-0000-0000-0000-000000000401"),
            subject=TicketSubject("App error"),
            message=TicketMessage("The app does not start."),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )

        decision = await provider.triage(ticket)

        assert decision.category is Category.TECHNICAL
        assert transport.requests[0].model == "test-model"
        assert "App error" in transport.requests[0].prompt

    asyncio.run(exercise())
