from datetime import datetime

from ai_ticket_triage.domain.tickets.errors import InvalidTicketStateError
from ai_ticket_triage.domain.tickets.value_objects import TicketStatus


class TicketTransitionPolicy:
    @staticmethod
    def validate(
        current_status: TicketStatus,
        current_updated_at: datetime,
        updated_at: datetime,
    ) -> None:
        if current_status is not TicketStatus.NEW:
            raise InvalidTicketStateError(
                f"Ticket cannot transition from terminal status '{current_status.value}'."
            )
        if updated_at < current_updated_at:
            raise InvalidTicketStateError("Transition time cannot move backwards.")
