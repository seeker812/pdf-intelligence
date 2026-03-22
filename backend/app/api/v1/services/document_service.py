import uuid
from typing import TYPE_CHECKING

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.chunk_entity import DocumentChunkEntity
from backend.app.api.v1.models.entities.document_entity import DocumentEntity
from backend.app.api.v1.models.entities.document_insight_entity import (
    DocumentInsightEntity,
)
from backend.app.api.v1.models.enums.document_status import DocumentStatus
from backend.app.api.v1.models.response import DocumentUploadResponse
from backend.app.api.v1.repository.document_repository import DocumentRepository
from backend.app.api.v1.dependencies.extraction_dependency import Container, container
from backend.app.core.exceptions import (
    AppBaseException,
    RecordNotFoundException,
    ConflictException,
)
from backend.app.utils.file_handler import FileHandler

if TYPE_CHECKING:
    from backend.app.api.v1.repository.chunk_repository import ChunkRepository
    from backend.app.api.v1.repository.insight_repository import InsightRepository
    from backend.app.extraction.rag.rag_service import RAGService

_CHAT_ENABLED_STATES = frozenset(
    {
        DocumentStatus.CHAT_READY,
        DocumentStatus.ANALYZING,
        DocumentStatus.COMPLETED,
    }
)

_ANALYSIS_READY_STATES = frozenset(
    {
        DocumentStatus.COMPLETED,
    }
)


class DocumentService:

    def __init__(self, di_container: Container = container) -> None:
        self._container = di_container
        self.document_repository: DocumentRepository = di_container.document_repository
        self.chunk_repository: "ChunkRepository" = di_container.chunk_repository
        self.insight_repository: "InsightRepository" = di_container.insight_repository

    @property
    def _processor(self):
        return self._container.document_processor

    @property
    def _rag_service(self) -> "RAGService":
        return self._container.rag_service

    def upload_document(
        self,
        background_tasks: BackgroundTasks,
        db: Session,
        file,
        user_id: str,
    ) -> DocumentUploadResponse:
        FileHandler.validate(file)

        document_id = str(uuid.uuid4())
        file_name = FileHandler.generate_file_name(file.filename, document_id)

        self.document_repository.create_document(
            db=db,
            document_id=document_id,
            file_name=file_name,
            status=DocumentStatus.UPLOADED,
            user_id=user_id,
        )

        file_path = self._container.storage_service.save_file(file, file_name)

        background_tasks.add_task(
            self._processor.process_document,
            document_id,
            file_path,
        )

        return DocumentUploadResponse(
            status=DocumentStatus.PROCESSING,
            document_id=document_id,
        )

    def list_documents(self, db: Session, user_id: str) -> list[DocumentEntity]:
        return self.document_repository.list_documents(db=db, user_id=user_id)

    def get_document(
        self,
        db: Session,
        document_id: str,
        user_id: str,
    ) -> DocumentEntity:
        document = self.document_repository.get_document(db=db, document_id=document_id)

        if document is None:
            raise RecordNotFoundException(message=f"Document '{document_id}' not found")

        if document.user_id != user_id:
            raise RecordNotFoundException(message=f"Document '{document_id}' not found")

        return document

    def ask_question(
        self, db: Session, document_id: str, question: str, user_id: str
    ) -> dict[str, object]:
        document = self.get_document(db=db, document_id=document_id, user_id=user_id)

        if document.status == DocumentStatus.FAILED:
            raise ConflictException(
                message="Document processing failed. Please re-upload the document."
            )

        if document.status not in _CHAT_ENABLED_STATES:
            raise ConflictException(
                message=(
                    f"Document is not ready for chat yet. "
                    f"Current status: {document.status.value}. "
                    f"Please wait for processing to complete."
                ),
            )

        return self._rag_service.ask(
            db=db,
            document_id=document_id,
            question=question,
        )

    def get_summary(self, db: Session, document_id: str) -> DocumentEntity:

        document = self.get_document(db=db, document_id=document_id)

        if document.status not in _ANALYSIS_READY_STATES:
            raise ConflictException(
                message=(
                    f"Analysis is not ready yet. "
                    f"Current status: {document.status.value}."
                )
            )

        return document

    def get_insights(
        self,
        db: Session,
        document_id: str,
        user_id: str,
    ) -> list[DocumentInsightEntity]:

        document = self.get_document(db=db, document_id=document_id, user_id=user_id)

        if document.status not in _ANALYSIS_READY_STATES:
            raise ConflictException(
                message=(
                    f"Analysis is not ready yet. "
                    f"Current status: {document.status.value}."
                )
            )

        return self.insight_repository.get_insights(
            db=db,
            document_id=document_id,
        )

    def get_chunks(
        self, db: Session, document_id: str, user_id: str
    ) -> list[DocumentChunkEntity]:
        self.get_document(
            db=db, document_id=document_id, user_id=user_id
        )  # existence check
        return self.chunk_repository.get_chunks(db=db, document_id=document_id)
