from ai_ticket_triage.domain.tickets.errors import EmptyTicketTextError, TicketTextTooLongError


class TicketTextValidationPolicy:
    @staticmethod
    def validate(field_name: str, value: str, max_length: int) -> None:
        if not value.strip():
            raise EmptyTicketTextError(f"Ticket {field_name} must not be empty.")
        if len(value) > max_length:
            raise TicketTextTooLongError(
                f"Ticket {field_name} must not exceed {max_length} characters."
            )
