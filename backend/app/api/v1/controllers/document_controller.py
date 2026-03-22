from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.chunk_entity import DocumentChunkEntity
from backend.app.api.v1.models.entities.document_entity import DocumentEntity
from backend.app.api.v1.models.entities.document_insight_entity import (
    DocumentInsightEntity,
)
from backend.app.api.v1.services.document_service import DocumentService


class DocumentController:
    def __init__(self, service: DocumentService | None = None) -> None:
        self.service = service or DocumentService()

    async def upload_document(
        self, db: Session, file, user_id: str, background_tasks: BackgroundTasks
    ):

        return self.service.upload_document(
            db=db, file=file, user_id=user_id, background_tasks=background_tasks
        )

    def list_documents(self, db: Session, user_id: str) -> list[DocumentEntity]:
        return self.service.list_documents(db=db, user_id=user_id)

    def get_document(
        self, db: Session, document_id: str, user_id: str
    ) -> DocumentEntity:
        return self.service.get_document(
            db=db, document_id=document_id, user_id=user_id
        )

    def get_insights(
        self, db: Session, document_id: str, user_id: str
    ) -> list[DocumentInsightEntity]:
        return self.service.get_insights(
            db=db, document_id=document_id, user_id=user_id
        )

    def get_chunks(
        self, db: Session, document_id: str, user_id: str
    ) -> list[DocumentChunkEntity]:
        return self.service.get_chunks(db=db, document_id=document_id, user_id=user_id)

    def ask_question(
        self, db: Session, document_id: str, question: str, user_id: str
    ) -> dict[str, object]:
        return self.service.ask_question(
            db=db, document_id=document_id, question=question, user_id=user_id
        )
