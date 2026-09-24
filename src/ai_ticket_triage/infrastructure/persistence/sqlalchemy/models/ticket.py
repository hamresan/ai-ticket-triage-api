from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, String
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
        CheckConstraint(
            "(status = 'triaged' AND category IS NOT NULL AND priority IS NOT NULL "
            "AND sentiment IS NOT NULL AND needs_human_review IS NOT NULL "
            "AND suggested_reply IS NOT NULL AND provenance IS NOT NULL) OR "
            "(status <> 'triaged' AND category IS NULL AND priority IS NULL "
            "AND sentiment IS NULL AND needs_human_review IS NULL "
            "AND suggested_reply IS NULL AND provenance IS NULL)",
            name="ck_tickets_decision_state",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(10_000), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(16), nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(16), nullable=True)
    needs_human_review: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    suggested_reply: Mapped[str | None] = mapped_column(String(4_000), nullable=True)
    provenance: Mapped[str | None] = mapped_column(String(16), nullable=True)
