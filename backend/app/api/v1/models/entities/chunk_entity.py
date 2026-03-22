from sqlalchemy import (
    Computed,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class DocumentChunkEntity(Base):
    __tablename__ = "document_chunks"
    chunk_id: Mapped[str] = mapped_column(String(64), primary_key=True)

    document_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "documents.documents.document_id", ondelete="CASCADE"
        ),  # ✅ schema.table.column
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk_text_tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', chunk_text)", persisted=True),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_document_chunks_doc_id_chunk_index", "document_id", "chunk_index"),
        Index(
            "ix_document_chunks_chunk_text_tsv",
            "chunk_text_tsv",
            postgresql_using="gin",
        ),
        {"schema": "documents"},
    )
