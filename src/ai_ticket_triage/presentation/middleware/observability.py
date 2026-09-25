import json
import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: object,
        *,
        provider: str,
        model: str | None,
        logger: logging.Logger | None = None,
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._provider = provider
        self._model = model
        self._logger = logger or logging.getLogger("ai_ticket_triage.request")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = perf_counter()
        response = await call_next(request)
        event = {
            "event": "request_completed",
            "request_id": str(request.state.request_id),
            "ticket_id": getattr(request.state, "ticket_id", None),
            "provider": self._provider,
            "model": self._model,
            "duration_ms": round((perf_counter() - started) * 1000, 3),
            "fallback_used": getattr(request.state, "fallback_used", None),
            "status_code": response.status_code,
        }
        self._logger.info(json.dumps(event, separators=(",", ":"), sort_keys=True))
        return response
