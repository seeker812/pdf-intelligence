import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "APP_ERROR") -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class DocumentProcessingError(Exception):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    @app.exception_handler(DocumentProcessingError)
    async def document_processing_error_handler(_: Request, exc: DocumentProcessingError) -> JSONResponse:
        logger.exception("Document processing error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": "DOCUMENT_PROCESSING_ERROR", "message": "Document processing failed"},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application exception")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred"},
            },
        )
