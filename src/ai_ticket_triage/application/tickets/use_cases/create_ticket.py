from collections.abc import Callable
from datetime import datetime
from uuid import UUID

from ai_ticket_triage.application.tickets.dto import CreateTicketInput, TicketCreationResult
from ai_ticket_triage.application.tickets.policies import TicketRequestFingerprint
from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject


class CreateTicket:
    def __init__(
        self,
        repository: TicketRepository,
        id_factory: Callable[[], UUID],
        clock: Callable[[], datetime],
        fingerprint: TicketRequestFingerprint,
    ) -> None:
        self._repository = repository
        self._id_factory = id_factory
        self._clock = clock
        self._fingerprint = fingerprint

    async def execute(self, data: CreateTicketInput) -> TicketCreationResult:
        now = self._clock()
        ticket = Ticket(
            id=self._id_factory(),
            subject=TicketSubject(data.subject),
            message=TicketMessage(data.message),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        return await self._repository.add_idempotent(
            ticket,
            data.idempotency_key,
            self._fingerprint.create(data.subject, data.message),
        )
