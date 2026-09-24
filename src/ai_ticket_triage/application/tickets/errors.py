from uuid import UUID


class TicketNotFoundError(Exception):
    def __init__(self, ticket_id: UUID) -> None:
        super().__init__(f"Ticket {ticket_id} was not found.")
