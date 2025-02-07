from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, CheckConstraint, text, ForeignKey, JSON
from datetime import datetime
from typing import Any

class Base(DeclarativeBase):
    pass


class PlatformORM(Base):
    __tablename__ = "platform"
    id: Mapped[int] = mapped_column(primary_key=True)
    platform_type: Mapped[str] = mapped_column(String(3))
    platform_name: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(256))


class UserORM(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey("platform.id"))
    name: Mapped[str] = mapped_column(String(256))
    icon_url: Mapped[str|None] = mapped_column(String(256))

class ChatORM(Base):
    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    icon_url: Mapped[str|None] = mapped_column(String(256))
    is_waiting_answer: Mapped[bool]
    is_archive: Mapped[bool]
    last_message_send_at: Mapped[datetime | None]
    platform_id: Mapped[int|None] = mapped_column(ForeignKey("platform.id"))

class ChatUsersORM(Base):
    __tablename__ = "chat_users"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"), primary_key=True, index=True)
    last_read_message_id: Mapped[int | None]
    user_in_chat: Mapped[bool]

class MessageORM(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"), index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    sended_at: Mapped[datetime]
    text: Mapped[str | None]
    attachments: Mapped[dict] = mapped_column(JSON)
    is_hide: Mapped[bool]  = mapped_column(Boolean, default=False)
    delete_at: Mapped[datetime | None] = None
    edit_data: Mapped[Any | None] = mapped_column(JSON, default= None)
    edit_at: Mapped[datetime | None] = None