import logging
from pathlib import Path

from backend.app.api.v1.repository.chunk_repository import ChunkRepository
from backend.app.api.v1.repository.document_repository import DocumentRepository
from backend.app.api.v1.repository.insight_repository import InsightRepository
from backend.app.core.database import SessionLocal
from backend.app.core.exceptions import DocumentProcessingError
from backend.app.extraction.pipeline.document_pipeline import DocumentPipeline

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(
        self,
        pipeline: DocumentPipeline,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        insight_repository: InsightRepository,
    ) -> None:
        self.pipeline = pipeline
        self.document_repo = document_repository
        self.chunk_repo = chunk_repository
        self.insight_repo = insight_repository

    def process_document(self, document_id: str, file_path: str) -> None:
        db = SessionLocal()
        logger.info("Background processing started for %s", document_id)

        try:
            result = self.pipeline.process_document(
                file_path=file_path,
                document_id=document_id,
            )

            chunks = result["chunks"]
            analysis = result["analysis"]

            self.chunk_repo.save_chunks(
                db=db,
                document_id=document_id,
                chunks=chunks,
            )

            self.insight_repo.save_insights(
                db=db,
                document_id=document_id,
                insights=analysis.key_insights,
            )

            updated_document = self.document_repo.update_analysis(
                db=db,
                document_id=document_id,
                analysis=analysis,
            )
            if updated_document is None:
                raise ValueError(f"Document {document_id} not found during processing")

            self.document_repo.update_status(
                db=db,
                document_id=document_id,
                status="COMPLETED",
            )
            logger.info("Background processing completed for %s", document_id)
        except Exception as exc:
            logger.exception("Document processing failed for %s", document_id)
            db.rollback()
            self.document_repo.update_status(
                db=db,
                document_id=document_id,
                status="FAILED",
            )
            raise DocumentProcessingError(f"Failed to process document {document_id}") from exc
        finally:
            db.close()
            Path(file_path).unlink(missing_ok=True)
