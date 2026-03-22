import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import router as api_router
from backend.app.core.config import get_settings
from backend.app.core.database import initialize_db
from backend.app.core.logging_config import setup_logging
from backend.app.middleware.exception_handler import ExceptionHandlerMiddleware
from backend.app.middleware.logger_middleware import LoggerMiddleware
from backend.app.middleware.requests_handler import ApiRequestHandler

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/docs/oauth2-redirect",
    "/openapi.json",
    "/redoc",
}

PUBLIC_PREFIXES = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting %s v%s [%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )
    initialize_db()
    logger.info("Database initialised")

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        # Hide docs in production — avoids exposing your API surface
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        ApiRequestHandler,
        public_paths=PUBLIC_PATHS,
        public_prefixes=PUBLIC_PREFIXES,
    )

    app.add_middleware(
        LoggerMiddleware,
        service_name="pdf-intelligence",
        fastapi_app=app,
    )

    app.add_middleware(ExceptionHandlerMiddleware)

    # ── Routes ────────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Health check ──────────────────────────────────────────────
    @app.get("/health", include_in_schema=False)
    def health() -> dict:
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
        }

    return app


app = create_app()
