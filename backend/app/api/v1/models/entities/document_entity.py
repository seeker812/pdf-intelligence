from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from backend.app.api.v1.models.enums.document_status import DocumentStatus
from backend.app.core.database import Base


class DocumentEntity(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(64), primary_key=True)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    document_type: Mapped[str | None] = mapped_column(String(255), nullable=True)

    category: Mapped[str | None] = mapped_column(String(255), nullable=True)

    short_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    detailed_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.UPLOADED,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "users.anonymous_users.user_id", ondelete="CASCADE"
        ),  # ✅ schema.table.column
        nullable=False,
    )

    __table_args__ = (
        Index("ix_documents_created_at", "created_at"),
        Index("ix_documents_user_id", "user_id"),
        {"schema": "documents"},
    )
