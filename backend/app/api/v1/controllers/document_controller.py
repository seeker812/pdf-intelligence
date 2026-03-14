from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.chunk_entity import DocumentChunkEntity
from backend.app.api.v1.models.entities.document_entity import DocumentEntity
from backend.app.api.v1.models.entities.document_insight_entity import DocumentInsightEntity
from backend.app.api.v1.services.document_service import DocumentService


class DocumentController:
    def __init__(self, service: DocumentService | None = None) -> None:
        self.service = service or DocumentService()

    def upload_document(
        self,
        background_tasks: BackgroundTasks,
        db: Session,
        file_path: str,
        file_name: str,
    ) -> dict[str, str]:
        return self.service.upload_document(
            background_tasks=background_tasks,
            db=db,
            file_path=file_path,
            file_name=file_name,
        )

    def list_documents(self, db: Session) -> list[DocumentEntity]:
        return self.service.list_documents(db=db)

    def get_document(self, db: Session, document_id: str) -> DocumentEntity:
        return self.service.get_document(db=db, document_id=document_id)

    def get_insights(self, db: Session, document_id: str) -> list[DocumentInsightEntity]:
        return self.service.get_insights(db=db, document_id=document_id)

    def get_chunks(self, db: Session, document_id: str) -> list[DocumentChunkEntity]:
        return self.service.get_chunks(db=db, document_id=document_id)

    def ask_question(
        self,
        db: Session,
        document_id: str,
        question: str,
    ) -> dict[str, object]:
        return self.service.ask_question(
            db=db,
            document_id=document_id,
            question=question,
        )
