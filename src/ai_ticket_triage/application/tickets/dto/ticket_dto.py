from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateTicketInput:
    subject: str
    message: str
