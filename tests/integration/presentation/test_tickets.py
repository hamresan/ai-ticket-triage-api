from pathlib import Path
from typing import cast

import httpx
import pytest
from alembic import command
from alembic.config import Config
from starlette.testclient import TestClient

from ai_ticket_triage.composition_root import build_application
from ai_ticket_triage.infrastructure.config import AppEnvironment, Settings


def build_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> httpx.Client:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'api.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config("alembic.ini"), "head")
    application = build_application(
        Settings(app_env=AppEnvironment.TEST, database_url=database_url)
    )
    return cast(httpx.Client, TestClient(application))


def test_create_retrieve_and_filter_ticket(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client = build_client(tmp_path, monkeypatch)
    response = client.post(
        "/api/v1/tickets",
        json={"subject": "Refund", "message": "Please refund my order."},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["status"] == "triaged"
    assert created["decision"]["provenance"] == "provider"
    assert created["decision"]["category"] == "technical"

    retrieved = client.get(f"/api/v1/tickets/{created['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == created

    matching = client.get("/api/v1/tickets", params={"status": "triaged"})
    assert matching.status_code == 200
    assert [item["id"] for item in matching.json()] == [created["id"]]
    assert client.get("/api/v1/tickets", params={"status": "new"}).json() == []


def test_invalid_request_uses_stable_error_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    response = client.post("/api/v1/tickets", json={"subject": " ", "message": "message"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == {
        "code": "validation_error",
        "message": "Request validation failed.",
    }
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_not_found_uses_stable_error_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    response = client.get(
        "/api/v1/tickets/00000000-0000-0000-0000-000000009999",
        headers={"X-Request-ID": "request-123"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "ticket_not_found", "message": "Ticket not found."},
        "request_id": "request-123",
    }


def test_invalid_status_filter_uses_validation_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    response = client.get("/api/v1/tickets", params={"status": "pending"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["request_id"]
