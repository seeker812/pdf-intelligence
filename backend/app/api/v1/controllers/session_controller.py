from sqlalchemy.orm import Session
from backend.app.api.v1.services.session_service import SessionService


class SessionController:

    def __init__(self):
        self.service = SessionService()

    def get_or_create_session(self, db: Session, user_id: str | None):

        return self.service.get_or_create_session(db=db, user_id=user_id)
