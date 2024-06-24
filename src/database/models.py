from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, CheckConstraint, text, ForeignKey, JSON
from datetime import datetime


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


class WaitingСhatORM(Base):
    __tablename__ = "unconnected_chat_with_bot"
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id"), primary_key=True)


class ChatORM(Base):
    __tablename__ = "chat"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))


class ChatUsersORM(Base):
    __tablename__ = "chat_users"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chat.id"), primary_key=True)


class MessageORM(Base):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    sended_at: Mapped[datetime]
    text: Mapped[str | None]
