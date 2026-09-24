"""Tests for the typed environment settings boundary."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_ticket_triage.infrastructure.config import AppEnvironment, Settings


def test_settings_have_safe_local_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_name == "AI Support Ticket Triage API"
    assert settings.app_env is AppEnvironment.LOCAL


def test_settings_parse_environment_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_NAME", "Environment Triage API")
    monkeypatch.setenv("APP_ENV", "test")

    settings = Settings()

    assert settings.app_name == "Environment Triage API"
    assert settings.app_env is AppEnvironment.TEST


def test_settings_reject_unknown_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_ENV", "unsupported")

    with pytest.raises(ValidationError):
        Settings()
