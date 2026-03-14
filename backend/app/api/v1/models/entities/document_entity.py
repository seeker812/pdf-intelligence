from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class DocumentEntity(Base):
    # The legacy CRUD layer already maps a `documents` table, so this SQL layer
    # uses its own table until the older model is retired or migrated.
    __tablename__ = "structured_documents"

    document_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    short_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    detailed_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="PROCESSING", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
