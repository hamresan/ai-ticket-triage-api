"""Dependency wiring and FastAPI application construction."""

from fastapi import FastAPI

from ai_ticket_triage.infrastructure.config import Settings
from ai_ticket_triage.presentation.routes import health_router


def build_application(settings: Settings) -> FastAPI:
    """Build the HTTP application from explicit dependencies."""
    application = FastAPI(title=settings.app_name)
    application.include_router(health_router)
    return application
