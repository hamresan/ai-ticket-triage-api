"""Dependency wiring and FastAPI application construction."""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI

from ai_ticket_triage.application.tickets.use_cases import CreateTicket, GetTicket, ListTickets
from ai_ticket_triage.infrastructure.config import Settings
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.database import (
    create_engine,
    create_session_factory,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyTicketRepository,
)
from ai_ticket_triage.presentation.errors import register_error_handlers
from ai_ticket_triage.presentation.middleware import RequestIdMiddleware
from ai_ticket_triage.presentation.routes import health_router, tickets_router


def build_application(settings: Settings) -> FastAPI:
    """Build the HTTP application from explicit dependencies."""
    engine = create_engine(settings.database_url)
    repository = SqlAlchemyTicketRepository(create_session_factory(engine))

    application = FastAPI(title=settings.app_name)
    application.state.engine = engine
    application.state.create_ticket = CreateTicket(repository, uuid4, lambda: datetime.now(UTC))
    application.state.get_ticket = GetTicket(repository)
    application.state.list_tickets = ListTickets(repository)
    application.add_middleware(RequestIdMiddleware)
    register_error_handlers(application)
    application.include_router(health_router)
    application.include_router(tickets_router)
    return application


def create_application() -> FastAPI:
    """Build the runtime application from environment-backed settings."""
    return build_application(Settings())
