"""ASGI application factory exposed to Uvicorn."""

from fastapi import FastAPI

from ai_ticket_triage.composition_root import create_application


def create_app() -> FastAPI:
    """Create the fully composed runtime application."""
    return create_application()
