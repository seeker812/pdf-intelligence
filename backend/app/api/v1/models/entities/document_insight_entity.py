from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class DocumentInsightEntity(Base):
    __tablename__ = "document_insights"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # insight_entity.py
    document_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "documents.documents.document_id", ondelete="CASCADE"
        ),  # ✅ schema.table.column
        nullable=False,
    )

    insight: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("ix_document_insights_document_id", "document_id"),
        {"schema": "documents"},
    )
