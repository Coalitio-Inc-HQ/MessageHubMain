from .models import *
from .schemes import *

from sqlalchemy import select, insert, text, func, bindparam, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
import datetime


async def platform_registration(session: AsyncSession, platform_type: str, platform_name: str, url: str) -> PlatformDTO:
    """
    Регестрирует новую платформу.
    Возаращяет: PlatformDTO(id,platform_type,platform_name,url).
    """
    res = (await session.execute(insert(PlatformORM).returning(PlatformORM.id).values(platform_type=platform_type, platform_name=platform_name, url=url))).scalar()
    await session.commit()
    return PlatformDTO(id=res, platform_type=platform_type, platform_name=platform_name, url=url)

async def get_platforms_by_name(session:AsyncSession,platform_name:str)->list[PlatformDTO]:
    """
    Получает платформы по имени.
    Возаращяет: PlatformDTO(id,platform_type,platform_name,url).
    """
    res = await session.execute(select(PlatformORM).where(PlatformORM.platform_name==platform_name))
    res_orm = res.scalars()
    res_dto = [PlatformDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto


async def update_platforms_by_name(session:AsyncSession,platform_name:str,url:str)->list[PlatformDTO]:
    """
    Обновляет url платформы, по имени.
    Возаращяет: PlatformDTO(id,platform_type,platform_name,url).
    """
    res = await session.execute(update(PlatformORM).where(PlatformORM.platform_name==platform_name).values(url=url).returning(PlatformORM))
    res_orm = res.scalars()
    res_dto = [PlatformDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    await session.commit()
    return res_dto


async def get_all_platform(session: AsyncSession) -> list[PlatformDTO]:
    """
    Получает все платформы.
    Возращяет PlatformDTO(id, platform_type,platform_name,url).
    """
    res = await session.execute(select(PlatformORM))
    res_orm = res.scalars()
    res_dto = [PlatformDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto


async def save_messege(session: AsyncSession, message: MessageDTO) -> MessageDTO:
    """
    Сохраняет сообщение в БД.
    Возвращяет: MessageDTO(id,chat_id,creator,created_at,sended_at,text_message).
    """
    message.sended_at = message.sended_at.astimezone(
        datetime.timezone.utc)
    res = await session.execute(insert(MessageORM).returning(MessageORM.id).values(chat_id=message.chat_id,
                                                                                   sender_id=message.sender_id,
                                                                                   sended_at=message.sended_at.replace(
                                                                                       tzinfo=None),
                                                                                   text=message.text))
    await session.commit()
    message.id = res.scalar()
    return message


async def get_users_by_chat_id(session: AsyncSession, chat_id: int) -> list[UserDTO]:
    """
    Получает всех пользователей чата.
    Возаращяет: [UserDTO(id,platform_id,name)].
    """
    res = await session.execute(select(UserORM).join(ChatUsersORM).where(ChatUsersORM.chat_id == chat_id))
    res_orm = res.scalars()
    res_dto = [UserDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto


async def get_platforms_by_chat_id(session: AsyncSession, chat_id: int) -> list[PlatformDTO]:
    """
    Получает все платформы по чату.
    Возращяет PlatformDTO(id, platform_type,platform_name,url).
    """
    subq1 = select(ChatUsersORM.user_id).where(
        ChatUsersORM.chat_id == chat_id).subquery()
    subq2 = select(UserORM.platform_id).where(UserORM.id.in_(subq1)).subquery()
    res = await session.execute(select(PlatformORM).where(PlatformORM.id.in_(subq2)))
    res_orm = res.scalars()
    res_dto = [PlatformDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto

"""
temp
"""


async def bot_user_registration(session: AsyncSession, platform_name: str, name: str) -> ChatUsersDTO:
    """
    Регестрирует новго пользователя и саздаёт новый чат в который его добавляет.
    Возвращяет: ChatUsersDTO(user.id,chat.id).
    """
    platform_id = (await session.execute(select(PlatformORM.id).where(PlatformORM.platform_name == platform_name))).scalar()
    bot_id = (await session.execute(insert(UserORM).returning(UserORM.id).values(platform_id=platform_id, name=name))).scalar()
    chat_id = (await session.execute(insert(ChatORM).returning(ChatORM.id).values(name=name))).scalar()
    await session.execute(insert(WaitingСhatORM).values(chat_id=chat_id))
    await session.execute(insert(ChatUsersORM).values(user_id=bot_id, chat_id=chat_id))
    await session.commit()
    return ChatUsersDTO(user_id=bot_id, chat_id=chat_id)
