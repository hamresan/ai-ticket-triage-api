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
from ai_ticket_triage.presentation.dependencies import TicketUseCases
from ai_ticket_triage.presentation.errors import register_error_handlers
from ai_ticket_triage.presentation.middleware import RequestIdMiddleware
from ai_ticket_triage.presentation.routes import create_ticket_router, health_router


def build_application(settings: Settings) -> FastAPI:
    """Build the HTTP application from explicit dependencies."""
    engine = create_engine(settings.database_url)
    repository = SqlAlchemyTicketRepository(create_session_factory(engine))
    ticket_use_cases = TicketUseCases(
        create=CreateTicket(repository, uuid4, lambda: datetime.now(UTC)),
        get=GetTicket(repository),
        list=ListTickets(repository),
    )

    def provide_ticket_use_cases() -> TicketUseCases:
        return ticket_use_cases

    application = FastAPI(title=settings.app_name)
    application.state.engine = engine
    application.add_middleware(RequestIdMiddleware)
    register_error_handlers(application)
    application.include_router(health_router)
    application.include_router(create_ticket_router(provide_ticket_use_cases))
    return application


def create_application() -> FastAPI:
    """Build the runtime application from environment-backed settings."""
    return build_application(Settings())
