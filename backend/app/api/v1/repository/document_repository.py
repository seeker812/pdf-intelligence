from typing import Any, cast

from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.document_entity import DocumentEntity
from backend.app.api.v1.models.enums.document_status import DocumentStatus


class DocumentRepository:

    def create_document(
        self,
        db: Session,
        document_id: str,
        file_name: str,
        status: DocumentStatus,
        user_id: str,
    ) -> DocumentEntity:

        doc = DocumentEntity(
            document_id=document_id,
            file_name=file_name,
            status=status,
            user_id=user_id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def get_document(self, db: Session, document_id: str) -> DocumentEntity | None:
        return (
            db.query(DocumentEntity)
            .filter(DocumentEntity.document_id == document_id)
            .first()
        )

    def list_documents(self, db: Session, user_id: str) -> list[DocumentEntity]:
        query = db.query(DocumentEntity).order_by(DocumentEntity.created_at.desc())
        query = query.filter(DocumentEntity.user_id == user_id)
        return query.all()

    def update_analysis(
        self,
        db: Session,
        document_id: str,
        analysis: Any,
    ) -> DocumentEntity:

        doc = self.get_document(db=db, document_id=document_id)
        if doc is None:
            raise ValueError(f"Document '{document_id}' not found")

        doc.document_type = analysis.document_type
        doc.category = analysis.category
        doc.short_summary = analysis.short_summary
        doc.detailed_summary = analysis.detailed_summary
        return doc

    def update_status(
        self,
        db: Session,
        document_id: str,
        status: DocumentStatus,
    ) -> DocumentEntity:

        doc = self.get_document(db=db, document_id=document_id)
        if doc is None:
            raise ValueError(f"Document '{document_id}' not found")

        doc.status = status
        db.commit()
        db.refresh(doc)
        return doc
