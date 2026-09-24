from collections.abc import Callable
from datetime import datetime

from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.application.triage.dto import TriageTicketInput
from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage.policies import DeterministicTriagePolicy


class TriageTicket:
    def __init__(
        self,
        repository: TicketRepository,
        provider: TriageProvider,
        fallback: DeterministicTriagePolicy,
        clock: Callable[[], datetime],
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._fallback = fallback
        self._clock = clock

    async def execute(self, data: TriageTicketInput) -> Ticket | None:
        ticket = await self._repository.get_by_id(data.ticket_id)
        if ticket is None:
            return None
        try:
            decision = await self._provider.triage(ticket)
        except TriageProviderError:
            decision = self._fallback.decide(ticket)
        triaged = ticket.mark_triaged(decision, updated_at=self._clock())
        await self._repository.update(triaged)
        return triaged
