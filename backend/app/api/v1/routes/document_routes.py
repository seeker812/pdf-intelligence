import logging
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    UploadFile,
    status,
    Header,
    Request,
)
from sqlalchemy.orm import Session

from backend.app.api.v1.controllers.document_controller import DocumentController
from backend.app.api.v1.dependencies.user_dependecy import get_current_user_id
from backend.app.api.v1.models.request import AskQuestionRequest
from backend.app.api.v1.models.response import (
    AskQuestionResponse,
    DocumentChunkResponse,
    DocumentInsightResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from backend.app.core.response_wrapper import response_wrapper
from backend.app.core.database import get_db

router = APIRouter()

controller = DocumentController()
logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
@response_wrapper
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):

    upload_response = await controller.upload_document(
        db=db, file=file, user_id=user_id, background_tasks=background_tasks
    )

    return upload_response, "Document uploaded successfully"


@router.get("", response_model=list[DocumentResponse])
@response_wrapper
async def list_documents(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.annon_id
    response = controller.list_documents(db=db, user_id=user_id)

    return response, "Documents retrieved successfully"


@router.get("/{document_id}", response_model=DocumentResponse)
@response_wrapper
async def get_document(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.state.annon_id
    response = controller.get_document(db=db, document_id=document_id, user_id=user_id)

    return response, "Document retrieved successfully"


@router.get("/{document_id}/insights", response_model=list[DocumentInsightResponse])
@response_wrapper
async def get_insights(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.state.annon_id
    response = controller.get_insights(db=db, document_id=document_id, user_id=user_id)

    return response, "Document insights retrieved successfully"


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
@response_wrapper
async def get_chunks(
    document_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.state.annon_id
    response = controller.get_chunks(db=db, document_id=document_id, user_id=user_id)

    return response, "Document chunks retrieved successfully"


@router.post("/{document_id}/ask", response_model=AskQuestionResponse)
@response_wrapper
async def ask_question(
    document_id: str,
    payload: AskQuestionRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.state.annon_id
    response = controller.ask_question(
        db=db,
        document_id=document_id,
        question=payload.question,
        user_id=user_id,
    )

    return response, "Question answered successfully"
