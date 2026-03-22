import uuid

from sqlalchemy.orm import Session

from backend.app.api.v1.models.response.session_response import SessionResponse
from backend.app.api.v1.repository.user_repository import UserRepository


class SessionService:

    def __init__(self):
        self.user_repository = UserRepository()

    def get_or_create_session(
        self, db: Session, user_id: str | None
    ) -> SessionResponse:

        if not user_id:

            new_user_id = str(uuid.uuid4())

            self.user_repository.create_user(db=db, user_id=new_user_id)

            return SessionResponse(user_id=new_user_id, is_new=True)

        user = self.user_repository.get_user(db, user_id)

        if user:

            self.user_repository.update_last_login(db, user)

            return SessionResponse(user_id=user_id, is_new=False)

        new_user_id = str(uuid.uuid4())

        self.user_repository.create_user(db=db, user_id=new_user_id)

        return SessionResponse(user_id=new_user_id, is_new=True)
