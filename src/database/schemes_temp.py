from pydantic import BaseModel, Field
from datetime import datetime


class ChatDTO_TEMP(BaseModel):
    id: int
    name: str = Field(max_length=256)


class ChatUsersDTO_TEMP(BaseModel):
    user_id: int
    chat_id: int


class MessageDTO_TEMP(BaseModel):
    id: int | None
    chat_id: int
    sender_id: int
    sended_at: datetime
    text: str | None


