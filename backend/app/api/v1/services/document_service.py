import uuid
from typing import TYPE_CHECKING

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.chunk_entity import DocumentChunkEntity
from backend.app.api.v1.models.entities.document_entity import DocumentEntity
from backend.app.api.v1.models.entities.document_insight_entity import DocumentInsightEntity
from backend.app.api.v1.repository.document_repository import DocumentRepository
from backend.app.core.dependency_injection import Container, container
from backend.app.core.exceptions import AppException

if TYPE_CHECKING:
    from app.api.v1.repository.chunk_repository import ChunkRepository
    from app.api.v1.repository.insight_repository import InsightRepository
    from app.extraction.rag.rag_service import RAGService


class DocumentService:
    def __init__(self, di_container: Container = container) -> None:
        self._container = di_container
        self.document_repository: DocumentRepository = di_container.document_repository
        self.chunk_repository: "ChunkRepository" = di_container.chunk_repository
        self.insight_repository: "InsightRepository" = di_container.insight_repository

    @property
    def processor(self):
        return self._container.document_processor

    @property
    def rag_service(self) -> "RAGService":
        return self._container.rag_service

    def upload_document(
        self,
        background_tasks: BackgroundTasks,
        db: Session,
        file_path: str,
        file_name: str,
    ) -> dict[str, str]:
        document_id = str(uuid.uuid4())

        self.document_repository.create_document(
            db=db,
            document_id=document_id,
            file_name=file_name,
        )

        background_tasks.add_task(
            self.processor.process_document,
            document_id,
            file_path,
        )

        return {
            "document_id": document_id,
            "status": "PROCESSING",
        }

    def list_documents(self, db: Session) -> list[DocumentEntity]:
        return self.document_repository.list_documents(db=db)

    def get_document(self, db: Session, document_id: str) -> DocumentEntity:
        document = self.document_repository.get_document(db=db, document_id=document_id)
        if document is None:
            raise AppException(
                message=f"Document {document_id} not found",
                status_code=404,
                code="DOCUMENT_NOT_FOUND",
            )
        return document

    def ask_question(
        self,
        db: Session,
        document_id: str,
        question: str,
    ) -> dict[str, object]:
        document = self.get_document(db=db, document_id=document_id)
        if document.status == "PROCESSING":
            raise AppException(
                message=f"Document {document_id} is still processing",
                status_code=409,
                code="DOCUMENT_PROCESSING",
            )
        if document.status == "FAILED":
            raise AppException(
                message=f"Document {document_id} processing failed",
                status_code=409,
                code="DOCUMENT_PROCESSING_FAILED",
            )
        if document.status != "COMPLETED":
            raise AppException(
                message=f"Document {document_id} is not ready for question answering",
                status_code=409,
                code="DOCUMENT_NOT_READY",
            )

        return self.rag_service.ask(
            db=db,
            document_id=document_id,
            question=question,
        )

    def get_insights(self, db: Session, document_id: str) -> list[DocumentInsightEntity]:
        self.get_document(db=db, document_id=document_id)
        return self.insight_repository.get_insights(db=db, document_id=document_id)

    def get_chunks(self, db: Session, document_id: str) -> list[DocumentChunkEntity]:
        self.get_document(db=db, document_id=document_id)
        return self.chunk_repository.get_chunks(db=db, document_id=document_id)
