"""Integration tests for the real FastAPI application and health endpoint."""

from typing import cast

import httpx
from starlette.testclient import TestClient

from ai_ticket_triage.composition_root import build_application
from ai_ticket_triage.infrastructure.config import AppEnvironment, Settings
from ai_ticket_triage.presentation.app import create_app


def test_health_endpoint_returns_ok() -> None:
    settings = Settings(app_name="Test Triage API", app_env=AppEnvironment.TEST)
    client = cast(httpx.Client, TestClient(build_application(settings)))

    try:
        response = client.get("/health")
    finally:
        client.close()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_application_uses_configured_title() -> None:
    settings = Settings(app_name="Configured Triage API", app_env=AppEnvironment.TEST)

    application = build_application(settings)

    assert application.title == "Configured Triage API"


def test_public_application_factory_builds_runnable_app() -> None:
    client = cast(httpx.Client, TestClient(create_app()))

    try:
        response = client.get("/health")
    finally:
        client.close()

    assert response.status_code == 200
