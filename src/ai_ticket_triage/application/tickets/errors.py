from uuid import UUID


class TicketNotFoundError(Exception):
    def __init__(self, ticket_id: UUID) -> None:
        super().__init__(f"Ticket {ticket_id} was not found.")


class IdempotencyConflictError(Exception):
    def __init__(self) -> None:
        super().__init__("Idempotency key was already used for a different request.")
