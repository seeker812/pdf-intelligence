from fastapi import Header, Depends, Request
from sqlalchemy.orm import Session

from backend.app.api.v1.services.session_service import SessionService
from backend.app.core.database import get_db
from backend.app.core.factories.services_factories import get_session_service


def get_current_user_id(
    request: Request,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
):
    user_id = request.state.annon_id
    session_response = session_service.get_or_create_session(db, user_id)
    return session_response.user_id
