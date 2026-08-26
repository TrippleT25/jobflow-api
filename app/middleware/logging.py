import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("jobflow.requests")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()

        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - started_at
        ) * 1000

        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        logger.info(
            "%s %s | status=%s | %.2fms | request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response
