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
    icon_url: str | None = Field(max_length=256)


class ChatDTO(BaseModel):
    id: int
    name: str = Field(max_length=256)
    is_waiting_answer: bool
    is_archive: bool
    icon_url: str | None = Field(max_length=256)
    last_message_send_at: datetime| None = None

class ExtChatDTO(ChatDTO):
    last_read_message_id: int | None = None
    user_in_chat: bool = False
    count_unredeble_messgaes: int | None = None


class ChatUsersDTO(BaseModel):
    user_id: int
    chat_id: int
    last_read_message_id: int | None = None
    user_in_chat: bool = False
    """
    last_read_message_id
    -1 = не установлено
    null зарезервироавно для опредления а состит ли пользователь в чате
    user_in_chat Пользователь находится в чате
    """


class MessageDTO(BaseModel):
    id: int | None
    chat_id: int
    sender_id: int
    sended_at: datetime
    text: str | None
    attachments: dict
