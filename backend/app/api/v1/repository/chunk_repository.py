import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.chunk_entity import DocumentChunkEntity


class ChunkRepository:
    def save_chunks(
        self,
        db: Session,
        document_id: str,
        chunks: list[str],
    ) -> list[DocumentChunkEntity]:
        entities: list[DocumentChunkEntity] = []

        for index, chunk_text in enumerate(chunks):
            chunk = DocumentChunkEntity(
                chunk_id=str(uuid.uuid4()),
                document_id=document_id,
                chunk_text=chunk_text,
                chunk_index=index,
            )
            entities.append(chunk)

        db.add_all(entities)
        db.commit()

        return entities

    def get_chunks(self, db: Session, document_id: str) -> list[DocumentChunkEntity]:
        return (
            db.query(DocumentChunkEntity)
            .filter(DocumentChunkEntity.document_id == document_id)
            .order_by(DocumentChunkEntity.chunk_index.asc())
            .all()
        )

    def search_chunks_by_keyword(
        self,
        db: Session,
        document_id: str,
        query: str,
        limit: int = 3,
    ) -> list[DocumentChunkEntity]:
        terms = [term.strip() for term in query.split() if len(term.strip()) >= 3]
        if not terms:
            terms = [query.strip()]

        if not any(terms):
            return []

        filters = [DocumentChunkEntity.chunk_text.ilike(f"%{term}%") for term in terms]

        return (
            db.query(DocumentChunkEntity)
            .filter(DocumentChunkEntity.document_id == document_id)
            .filter(or_(*filters))
            .order_by(DocumentChunkEntity.chunk_index.asc())
            .limit(limit)
            .all()
        )
