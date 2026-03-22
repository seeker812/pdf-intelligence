from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.api.v1.controllers.session_controller import SessionController
from backend.app.api.v1.models.response.session_response import SessionResponse

router = APIRouter()
controller = SessionController()


@router.get("", response_model=SessionResponse)
def get_or_create_session(
    request: Request,
    db: Session = Depends(get_db),
):
    user_id = request.state.annon_id
    return controller.get_or_create_session(db=db, user_id=user_id)
