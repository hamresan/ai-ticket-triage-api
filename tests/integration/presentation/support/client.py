from pathlib import Path
from typing import cast

import httpx
import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from starlette.testclient import TestClient

from ai_ticket_triage.composition_root import build_application
from ai_ticket_triage.infrastructure.config import AppEnvironment, Settings


def build_test_application(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'api.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config("alembic.ini"), "head")
    settings = Settings(
        _env_file=None,
        app_env=AppEnvironment.TEST,
        database_url=database_url,
    )
    return build_application(settings)


def build_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> httpx.Client:
    return cast(httpx.Client, TestClient(build_test_application(tmp_path, monkeypatch)))
