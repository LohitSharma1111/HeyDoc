import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        started = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            latency_ms = int((time.perf_counter() - started) * 1000)
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "user_id": getattr(request.state, "user_id", "unknown"),
                    "latency_ms": latency_ms,
                },
            )
            raise

        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "user_id": getattr(request.state, "user_id", "unknown"),
                "latency_ms": latency_ms,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response

