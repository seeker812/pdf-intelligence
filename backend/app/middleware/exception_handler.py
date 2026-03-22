import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.exceptions import AppBaseException, ErrorCode, ErrorStatus

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except AppBaseException as exc:
            logger.warning(
                "[%s] %s | path=%s method=%s",
                exc.code,
                exc.message,
                request.url.path,
                request.method,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": exc.code,
                        "message": exc.message,
                    },
                },
            )

        except Exception as exc:
            logger.exception(
                "Unhandled exception | path=%s method=%s error=%s",
                request.url.path,
                request.method,
                str(exc),
            )
            return JSONResponse(
                status_code=ErrorStatus.INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": {
                        "code": ErrorCode.INTERNAL_SERVER_ERROR,
                        "message": "An unexpected error occurred",
                    },
                },
            )
