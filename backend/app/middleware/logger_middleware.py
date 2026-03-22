import logging
import time
import uuid

from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request_logger")


def _log_routes(app: FastAPI) -> None:
    logger.info("━" * 60)
    logger.info("Registered API routes:")
    logger.info("━" * 60)
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ", ".join(sorted(route.methods))
            logger.info("  %-8s %s", methods, route.path)
    logger.info("━" * 60)


class LoggerMiddleware(BaseHTTPMiddleware):

    def __init__(
        self, app, service_name: str = "pdf-intelligence", fastapi_app=None
    ) -> None:
        super().__init__(app)
        self.service_name = service_name
        if fastapi_app:
            _log_routes(fastapi_app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]  # short unique id per request
        start = time.perf_counter()

        logger.info(
            "→ [%s] %s %s [%s]",
            request_id,
            request.method,
            request.url.path,
            self.service_name,
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "← [%s] %s %s → %s (%.2fms) [%s]",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            self.service_name,
        )

        response.headers["X-Request-ID"] = request_id

        return response
