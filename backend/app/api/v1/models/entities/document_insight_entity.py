from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class DocumentInsightEntity(Base):
    __tablename__ = "document_insights"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("structured_documents.document_id"),
        nullable=False,
        index=True,
    )
    insight: Mapped[str] = mapped_column(Text, nullable=False)
