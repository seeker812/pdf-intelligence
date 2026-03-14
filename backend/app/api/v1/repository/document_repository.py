from typing import Any

from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.document_entity import DocumentEntity


class DocumentRepository:
    def create_document(
        self,
        db: Session,
        document_id: str,
        file_name: str,
        status: str = "PROCESSING",
    ) -> DocumentEntity:
        doc = DocumentEntity(
            document_id=document_id,
            file_name=file_name,
            status=status,
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

    def list_documents(self, db: Session) -> list[DocumentEntity]:
        return db.query(DocumentEntity).order_by(DocumentEntity.created_at.desc()).all()

    def update_analysis(
        self,
        db: Session,
        document_id: str,
        analysis: Any,
    ) -> DocumentEntity | None:
        doc = self.get_document(db=db, document_id=document_id)
        if doc is None:
            return None

        doc.document_type = analysis.document_type
        doc.category = analysis.category
        doc.short_summary = analysis.short_summary
        doc.detailed_summary = analysis.detailed_summary

        db.commit()
        db.refresh(doc)

        return doc

    def update_status(
        self,
        db: Session,
        document_id: str,
        status: str,
    ) -> DocumentEntity | None:
        doc = self.get_document(db=db, document_id=document_id)
        if doc is None:
            return None

        doc.status = status

        db.commit()
        db.refresh(doc)

        return doc
