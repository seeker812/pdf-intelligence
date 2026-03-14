import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_router
from app.core.config import get_settings
from app.core.database import initialize_db
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging
from app.middleware.logger_middleware import LoggerMiddleware
from app.middleware.requests_handler import ApiRequestHandler

setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()
SERVICE_NAME = "pdf-intelligence"


def create_app() -> FastAPI:
    app = FastAPI(title="AI Document Intelligence API", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    app.add_middleware(
        ApiRequestHandler,
        public_paths={"/health", "/docs", "/docs/oauth2-redirect", "/openapi.json", "/redoc"},
        public_prefixes={"/documents"},
    )
    app.add_middleware(LoggerMiddleware, service_name=SERVICE_NAME)

    register_exception_handlers(app)

    @app.on_event("startup")
    def on_startup() -> None:
        initialize_db()
        logger.info("Database initialized")

    return app


app = create_app()
