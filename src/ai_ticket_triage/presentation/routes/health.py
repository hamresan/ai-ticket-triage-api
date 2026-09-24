"""Health-check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Public health-check response."""

    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Return process-level health for local and container checks."""
    return HealthResponse(status="ok")
