from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ai_ticket_triage.domain.tickets import TicketStatus


class CreateTicketRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=10_000)


class TicketResponse(BaseModel):
    id: UUID
    subject: str
    message: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
