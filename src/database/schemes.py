from pydantic import BaseModel, Field
from datetime import datetime


class PlatformDTO(BaseModel):
    id: int
    platform_type: str = Field(max_length=3)
    platform_name: str = Field(max_length=30)
    url: str = Field(max_length=256)


class UserDTO(BaseModel):
    id: int
    platform_id: int
    name: str = Field(max_length=256)


class WaitingСhatDTO(BaseModel):
    chat_id: int


class ChatDTO(BaseModel):
    id: int
    name: str = Field(max_length=256)


class ChatUsersDTO(BaseModel):
    user_id: int
    chat_id: int


class MessageDTO(BaseModel):
    id: int|None
    chat_id: int
    sender_id: int
    sended_at: datetime
    text: str | None
