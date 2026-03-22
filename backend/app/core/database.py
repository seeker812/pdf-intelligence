import logging
from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class Base(DeclarativeBase):
    pass


if settings.is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        future=True,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        future=True,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
    )

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


def _set_search_path(conn, _branch):
    cursor = conn.cursor()
    cursor.execute("SET search_path TO documents, users, public")
    cursor.close()


if not settings.is_sqlite:
    event.listen(engine, "connect", _set_search_path)


def initialize_db() -> None:
    """
    Imports all entity classes so SQLAlchemy metadata is populated.
    Schemas and tables must already exist (created via schema.sql).
    Does NOT create or modify any database objects at runtime.
    """
    from backend.app.api.v1.models.entities.user_entity import UserEntity  # noqa: F401
    from backend.app.api.v1.models.entities.document_entity import (
        DocumentEntity,
    )  # noqa: F401
    from backend.app.api.v1.models.entities.chunk_entity import (
        DocumentChunkEntity,
    )  # noqa: F401
    from backend.app.api.v1.models.entities.document_insight_entity import (
        DocumentInsightEntity,
    )  # noqa: F401

    logger.info("Entity metadata loaded")

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connected successfully ✓ (%s)", settings.DATABASE_URL)
    except Exception as exc:
        logger.error("Database connection failed ✗ — %s", exc)
        raise


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
