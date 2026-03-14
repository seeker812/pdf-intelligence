from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)


def initialize_db() -> None:
    # Import models so SQLAlchemy metadata is populated before create_all.
    from app.models import document  # noqa: F401
    from app.api.v1.models import entities  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _sync_structured_document_schema()


def _sync_structured_document_schema() -> None:
    inspector = inspect(engine)
    if "structured_documents" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("structured_documents")}

    with engine.begin() as connection:
        if "status" not in column_names:
            connection.execute(text("ALTER TABLE structured_documents ADD COLUMN status VARCHAR(32)"))

        connection.execute(
            text("UPDATE structured_documents SET status = 'COMPLETED' WHERE status IS NULL")
        )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
