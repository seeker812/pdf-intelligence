from pydantic import BaseModel


class SessionResponse(BaseModel):
    user_id: str
    is_new: bool
