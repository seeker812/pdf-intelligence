from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.api.v1.models.entities.user_entity import UserEntity


class UserRepository:

    def get_user(self, db: Session, user_id: str):

        return db.query(UserEntity).filter(UserEntity.user_id == user_id).first()

    def create_user(self, db: Session, user_id: str):

        user = UserEntity(user_id=user_id)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def update_last_login(self, db: Session, user: UserEntity):

        user.last_login = datetime.utcnow()
        db.commit()
