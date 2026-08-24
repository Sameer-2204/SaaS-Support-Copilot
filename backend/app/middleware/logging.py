"""Request logging middleware for FastAPI.

Logs method, path, status code, and response time for every request.
Adds X-Request-ID header for tracing.
"""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("saas_copilot")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request with timing and a unique request ID."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        logger.info(f"[{request_id}] → {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.error(f"[{request_id}] ✗ 500 {duration:.0f}ms — {str(e)}")
            raise

        duration = (time.time() - start) * 1000
        logger.info(f"[{request_id}] ← {response.status_code} {duration:.0f}ms")

        response.headers["X-Request-ID"] = request_id
        return response
