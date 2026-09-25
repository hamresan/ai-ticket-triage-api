"""Integration tests for the real FastAPI application and health endpoint."""

import asyncio

import httpx

from ai_ticket_triage.composition_root import build_application
from ai_ticket_triage.infrastructure.config import AppEnvironment, Settings
from ai_ticket_triage.presentation.app import create_app


def test_health_endpoint_returns_ok() -> None:
    application = build_application(
        Settings(app_name="Test Triage API", app_env=AppEnvironment.TEST)
    )

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    asyncio.run(exercise())


def test_application_uses_configured_title() -> None:
    settings = Settings(app_name="Configured Triage API", app_env=AppEnvironment.TEST)

    application = build_application(settings)

    assert application.title == "Configured Triage API"


def test_public_application_factory_builds_runnable_app() -> None:
    application = create_app()

    async def exercise() -> None:
        transport = httpx.ASGITransport(app=application)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200

    asyncio.run(exercise())
