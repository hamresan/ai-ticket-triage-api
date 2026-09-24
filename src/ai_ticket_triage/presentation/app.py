"""ASGI application factory exposed to Uvicorn."""

from fastapi import FastAPI

from ai_ticket_triage.composition_root import build_application
from ai_ticket_triage.infrastructure.config import Settings


def create_app() -> FastAPI:
    """Create the application using the runtime settings boundary."""
    return build_application(Settings())
