import uuid
from typing import cast

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.chunk_entity import DocumentChunkEntity


class ChunkRepository:

    def save_chunks(
        self,
        db: Session,
        document_id: str,
        chunks: list[str],
    ) -> list[DocumentChunkEntity]:

        entities = [
            DocumentChunkEntity(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_text=chunk_text,
                chunk_index=index,
            )
            for index, chunk_text in enumerate(chunks)
        ]
        db.add_all(entities)
        return entities

    def get_chunks(self, db: Session, document_id: str) -> list[DocumentChunkEntity]:
        return cast(
            list[DocumentChunkEntity],
            db.query(DocumentChunkEntity)
            .filter(DocumentChunkEntity.document_id == document_id)
            .order_by(DocumentChunkEntity.chunk_index.asc())
            .all(),
        )

    def search_chunks_by_keyword(
        self,
        db: Session,
        document_id: str,
        query: str,
        limit: int = 3,
    ) -> list[DocumentChunkEntity]:

        if not query.strip():
            return []

        tsquery = func.plainto_tsquery("english", query)

        return cast(
            list[DocumentChunkEntity],
            db.query(DocumentChunkEntity)
            .filter(DocumentChunkEntity.document_id == document_id)
            .filter(DocumentChunkEntity.chunk_text_tsv.op("@@")(tsquery))
            .order_by(func.ts_rank(DocumentChunkEntity.chunk_text_tsv, tsquery).desc())
            .limit(limit)
            .all(),
        )
