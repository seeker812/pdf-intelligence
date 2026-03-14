import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.api.v1.controllers.document_controller import DocumentController
from backend.app.api.v1.models.request import AskQuestionRequest
from backend.app.api.v1.models.response import (
    AskQuestionResponse,
    DocumentChunkResponse,
    DocumentInsightResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from backend.app.core.database import get_db
from backend.app.core.exceptions import AppException
from backend.app.utils.file_utils import save_uploaded_file

router = APIRouter()
controller = DocumentController()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise AppException(message="Uploaded file must have a filename", status_code=400, code="INVALID_FILE")

    file_path: str | None = None

    try:
        logger.info("Uploading document %s", file.filename)
        file_path = save_uploaded_file(file)
        return controller.upload_document(
            background_tasks=background_tasks,
            db=db,
            file_path=file_path,
            file_name=file.filename,
        )
    except Exception:
        logger.exception("Failed to upload document %s", file.filename)
        if file_path is not None:
            Path(file_path).unlink(missing_ok=True)
        raise
    finally:
        await file.close()


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return controller.list_documents(db=db)


@router.get("/{document_id}/insights", response_model=list[DocumentInsightResponse])
def get_insights(document_id: str, db: Session = Depends(get_db)):
    return controller.get_insights(db=db, document_id=document_id)


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
def get_chunks(document_id: str, db: Session = Depends(get_db)):
    return controller.get_chunks(db=db, document_id=document_id)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    return controller.get_document(db=db, document_id=document_id)


@router.post("/{document_id}/ask", response_model=AskQuestionResponse)
def ask_question(
    document_id: str,
    payload: AskQuestionRequest,
    db: Session = Depends(get_db),
):
    logger.info("Question received for document %s", document_id)
    return controller.ask_question(
        db=db,
        document_id=document_id,
        question=payload.question,
    )
