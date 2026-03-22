import logging
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from backend.app.api.v1.models.enums.document_status import DocumentStatus
from backend.app.api.v1.repository.chunk_repository import ChunkRepository
from backend.app.api.v1.repository.document_repository import DocumentRepository
from backend.app.api.v1.repository.insight_repository import InsightRepository
from backend.app.core.exceptions import DocumentProcessingError
from backend.app.extraction.pipeline.document_pipeline import DocumentPipeline

logger = logging.getLogger(__name__)

SessionFactory = Callable[[], Session]


class DocumentProcessor:
    """
    Orchestrates two-phase background document processing.

    ┌─────────────────────────────────────────────────────────┐
    │  Phase 1  PROCESSING → CHAT_READY                       │
    │                                                         │
    │  parse_and_chunk()  ──► chunks + clean_text             │
    │         │                                               │
    │         ├──► Thread A: embed_and_store()  (I/O bound)   │
    │         └──► Thread B: save_chunks_to_db() (I/O bound)  │
    │                                                         │
    │  wait(FIRST_EXCEPTION) → both must succeed              │
    │  → status = CHAT_READY  → user unblocked for chat       │
    └─────────────────────────────────────────────────────────┘
    ┌─────────────────────────────────────────────────────────┐
    │  Phase 2  ANALYSING → COMPLETED                         │
    │                                                         │
    │  status = ANALYSING                                     │
    │  run_phase_two()  (MAP threads inside DocumentAnalyzer) │
    │  → persist insights + analysis fields                   │
    │  → status = COMPLETED                                   │
    └─────────────────────────────────────────────────────────┘

    """

    def __init__(
        self,
        pipeline: DocumentPipeline,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        insight_repository: InsightRepository,
        session_factory: SessionFactory,
    ) -> None:
        self.pipeline = pipeline
        self.document_repo = document_repository
        self.chunk_repo = chunk_repository
        self.insight_repo = insight_repository
        self.session_factory = session_factory

    def process_document(self, document_id: str, file_path: str) -> None:
        logger.info("Background task started document_id=%s", document_id)
        phase_one_result = self._run_phase_one(
            document_id=document_id, file_path=file_path
        )
        self._run_phase_two(
            document_id=document_id,
            clean_text=phase_one_result["clean_text"],
        )
        logger.info("Background task complete document_id=%s", document_id)

    def _run_phase_one(self, document_id: str, file_path: str) -> dict:
        db: Session = self.session_factory()
        try:
            parse_result = self.pipeline.parse_and_chunk(
                file_path=file_path,
                document_id=document_id,
            )
            chunks: list[str] = parse_result["chunks"]
            clean_text: str = parse_result["clean_text"]

            with ThreadPoolExecutor(
                max_workers=2, thread_name_prefix="phase1"
            ) as executor:
                embed_future = executor.submit(
                    self.pipeline.embed_and_store, chunks, document_id
                )
                db_future = executor.submit(
                    self._save_chunks_in_thread, document_id, chunks
                )

                done, _ = wait([embed_future, db_future], return_when=FIRST_EXCEPTION)

                for future in done:
                    future.result()

            logger.info("Phase 1 parallel steps complete document_id=%s", document_id)

            self.document_repo.update_status(
                db=db,
                document_id=document_id,
                status=DocumentStatus.CHAT_READY,
            )

            Path(file_path).unlink(missing_ok=True)
            logger.debug("Temp file removed path=%s", file_path)

            return {"clean_text": clean_text}

        except Exception as exc:
            logger.exception("Phase 1 failed document_id=%s", document_id)
            db.rollback()
            db.close()
            self._mark_failed(document_id)
            raise DocumentProcessingError(
                f"Phase 1 failed for document '{document_id}'"
            ) from exc
        finally:
            db.close()

    def _save_chunks_in_thread(self, document_id: str, chunks: list[str]) -> None:
        """
        Saves chunk rows to Postgres in a thread-local session.

        Must open its own session — SQLAlchemy sessions are not thread-safe.
        The main thread's session must never be passed into this method.
        """
        thread_db: Session = self.session_factory()
        try:
            self.chunk_repo.save_chunks(
                db=thread_db,
                document_id=document_id,
                chunks=chunks,
            )
            thread_db.commit()
            logger.info(
                "Chunks saved document_id=%s count=%d",
                document_id,
                len(chunks),
            )
        except Exception:
            thread_db.rollback()
            raise
        finally:
            thread_db.close()

    def _run_phase_two(self, document_id: str, clean_text: str) -> None:
        db: Session = self.session_factory()

        # Signal to frontend that analysis is in progress
        self.document_repo.update_status(
            db=db,
            document_id=document_id,
            status=DocumentStatus.ANALYZING,
        )

        try:
            # DocumentAnalyzer manages MAP threads internally
            analysis = self.pipeline.run_phase_two(
                clean_text=clean_text,
                document_id=document_id,
            )

            # Stage insights + analysis fields then commit atomically
            self.insight_repo.save_insights(
                db=db,
                document_id=document_id,
                insights=analysis.key_insights,
            )
            self.document_repo.update_analysis(
                db=db,
                document_id=document_id,
                analysis=analysis,
            )
            db.commit()
            logger.info("Analysis committed document_id=%s", document_id)

            self.document_repo.update_status(
                db=db,
                document_id=document_id,
                status=DocumentStatus.COMPLETED,
            )

        except Exception as exc:
            logger.exception("Phase 2 failed document_id=%s", document_id)
            db.rollback()
            db.close()
            # Vectors are in Qdrant — chat still works even if analysis failed
            self._mark_failed(document_id)
            raise DocumentProcessingError(
                f"Phase 2 failed for document '{document_id}'"
            ) from exc
        finally:
            db.close()

    # ------------------------------------------------------------------
    # Recovery
    # ------------------------------------------------------------------

    def _mark_failed(self, document_id: str) -> None:
        """
        Opens a fresh independent session to write FAILED status.
        Always called after the main session has been rolled back and closed
        so we never write to a post-rollback session.
        """
        recovery_db: Session = self.session_factory()
        try:
            self.document_repo.update_status(
                db=recovery_db,
                document_id=document_id,
                status=DocumentStatus.FAILED,
            )
            logger.info("Marked FAILED document_id=%s", document_id)
        except Exception:
            logger.exception(
                "Could not mark FAILED document_id=%s — manual intervention required",
                document_id,
            )
        finally:
            recovery_db.close()
