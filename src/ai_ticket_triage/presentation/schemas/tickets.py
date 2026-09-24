from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai_ticket_triage.domain.tickets import TicketStatus


class CreateTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=10_000)

    @field_validator("subject", "message")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class TicketResponse(BaseModel):
    id: UUID
    subject: str
    message: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
