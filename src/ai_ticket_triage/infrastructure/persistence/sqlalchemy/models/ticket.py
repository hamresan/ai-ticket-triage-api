from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models.base import Base


class TicketModel(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint("length(trim(subject)) > 0", name="ck_tickets_subject_not_blank"),
        CheckConstraint("length(subject) <= 200", name="ck_tickets_subject_length"),
        CheckConstraint("length(trim(message)) > 0", name="ck_tickets_message_not_blank"),
        CheckConstraint("length(message) <= 10000", name="ck_tickets_message_length"),
        CheckConstraint("status IN ('new', 'triaged', 'failed')", name="ck_tickets_status"),
        CheckConstraint("updated_at >= created_at", name="ck_tickets_timestamps"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(10_000), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
