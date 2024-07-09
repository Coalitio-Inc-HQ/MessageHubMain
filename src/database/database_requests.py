from .models import *
from .schemes import *

from sqlalchemy import select, insert, text, func, bindparam, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
import datetime


async def platform_registration(session: AsyncSession, platform_type: str, platform_name: str, url: str) -> PlatformDTO:
    """
    Регистрирует новую платформу.
    Возаращяет: PlatformDTO(id,platform_type,platform_name,url).
    """
    res = (await session.execute(insert(PlatformORM).returning(PlatformORM.id).values(platform_type=platform_type, platform_name=platform_name, url=url))).scalar()
    await session.commit()
    return PlatformDTO(id=res, platform_type=platform_type, platform_name=platform_name, url=url)


async def get_platforms_by_name(session: AsyncSession, platform_name: str) -> list[PlatformDTO]:
    """
    Получает платформы по имени.
    Возаращяет: PlatformDTO(id,platform_type,platform_name,url).
    """
    res = await session.execute(select(PlatformORM).where(PlatformORM.platform_name == platform_name))
    res_orm = res.scalars()
    res_dto = [PlatformDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto


async def update_platforms_by_name(session: AsyncSession, platform_name: str, url: str) -> list[PlatformDTO]:
    """
    Обновляет url платформы, по имени.
    Возаращяет: PlatformDTO(id,platform_type,platform_name,url).
    """
    res = await session.execute(update(PlatformORM).where(PlatformORM.platform_name == platform_name).values(url=url).returning(PlatformORM))
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


async def get_list_of_waiting_chats(session: AsyncSession,count:int) -> list[ChatDTO]:
    """
    Возращяет список всех ожидающих чатов.
    """
    res = None
    if count<0:
        res = await session.execute(select(ChatORM).join(WaitingСhatORM))
    else:
        res = await session.execute(select(ChatORM).join(WaitingСhatORM).limit(count))
    res_orm = res.scalars()
    res_dto = [ChatDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto


async def connect_user_to_chat(session: AsyncSession,user_id: int, chat_id: int) -> ChatUsersDTO:
    """
    Добавлет ползователя к указаному чату.
    Возвращяет: ChatUsersDTO(user.id,chat.id).
    """
    session.add(ChatUsersORM(user_id=user_id, chat_id=chat_id))
    await session.commit()
    return ChatUsersDTO(user_id=user_id, chat_id=chat_id)


async def get_chats_by_user_id(session: AsyncSession, user_id: int) -> list[ChatDTO]:
    """
    Получает все чаты пользователя. 
    Возаращяет: [ChatDTO(id,name)].
    """
    res = await session.execute(select(ChatORM).join(ChatUsersORM).where(ChatUsersORM.user_id == user_id))
    res_orm = res.scalars()
    res_dto = [ChatDTO.model_validate(
        row, from_attributes=True) for row in res_orm]
    return res_dto

async def get_messges_from_chat(session: AsyncSession,chat_id: int, count:int,offset_message_id:int) -> list[MessageDTO]:
    """
    Возращяет count последних сообщений из чата, отсортированных по датте.
    Возвращяет: list[MessageDTO(id,chat_id,creator,created_at,edit_at,text_message)].
    """
    res = None

    if offset_message_id<0:
        res = await session.execute(select(MessageORM).where(MessageORM.chat_id == chat_id).order_by(MessageORM.sended_at.desc(),MessageORM.id.desc()).limit(count))
    else:
        subq = select(MessageORM.sended_at).where(MessageORM.id==offset_message_id).scalar_subquery()
        res = await session.execute(select(MessageORM).where(MessageORM.chat_id == chat_id,MessageORM.sended_at<=subq).order_by(MessageORM.sended_at.desc(),MessageORM.id.desc()).limit(count))
    res_orm = res.scalars().all()
    res_dto = [MessageDTO.model_validate(
        row, from_attributes=True) for row in res_orm[::-1]]
    return res_dto


async def get_chat_by_id(session: AsyncSession, chat_id: int) -> ChatDTO:
    """
    Получает чат по id.
    """
    res = (await session.execute(select(ChatORM).where(ChatORM.id == chat_id))).scalar()
    return ChatDTO.model_validate(res, from_attributes=True)


async def get_platform_by_user_id(session: AsyncSession, user_id: int) -> PlatformDTO:
    """
    Получает платфолрму по user_id.
    """
    subq = select(UserORM.platform_id).where(UserORM.id==user_id).scalar_subquery()
    res = (await session.execute(select(PlatformORM).where(PlatformORM.id == subq))).scalar()
    return PlatformDTO.model_validate(res, from_attributes=True)


async def get_users_by_chat_id(session: AsyncSession, chat_id: int)->list[UserDTO]:
    """
    Получает всех пользователей чата
    """
    subq1 = select(ChatUsersORM.user_id).where(
        ChatUsersORM.chat_id == chat_id).subquery()
    subq2 = select(UserORM).where(UserORM.id.in_(subq1))
    res = await session.execute(subq2)
    res_orm = res.scalars()
    res_dto = [UserDTO.model_validate(row, from_attributes=True) for row in res_orm]
    return res_dto

async def whether_the_user_is_in_the_chat(session: AsyncSession,user_id:int,chat_id:int)->bool:
    """
    Проверяем принадлежит ли пользователдь чату
    """
    res = await( session.execute(select(func.count()).where(ChatUsersORM.chat_id==chat_id,ChatUsersORM.user_id==user_id)))
    if (res.scalar()==1):
        return True
    else:
        return False


async def is_waiting_chat(session: AsyncSession,chat_id:int)->bool:
    """
    Проверяем является ли чат ожидающим
    """
    res = await( session.execute(select(func.count()).where(WaitingСhatORM.chat_id == chat_id)))
    if (res.scalar()==1):
        return True
    else:
        return False

async def get_user_by_user_id(session: AsyncSession,user_id:int) -> UserDTO:
    """
    Получаем пользователя по id
    """
    res = await(session.execute(select(UserORM).where(UserORM.id==user_id)))
    return UserDTO.model_validate(res.scalar(),from_attributes=True)

"""
temp
"""


async def connect_to_a_waiting_chat(session: AsyncSession, user_id: int, chat_id: int) -> ChatDTO:
    """
    Подключат пользователя к ожидающему чату.
    """
    await session.execute(insert(ChatUsersORM).values(user_id=user_id, chat_id=chat_id))
    await session.execute(delete(WaitingСhatORM).where(WaitingСhatORM.chat_id == chat_id))
    res = (await session.execute(select(ChatORM).where(ChatORM.id == chat_id))).scalar()
    res = ChatDTO.model_validate(res, from_attributes=True)
    await session.commit()
    return res


async def user_registration(session: AsyncSession, platform_name: str, name: str) -> UserDTO:
    """
    Регистрирует нового пользователя с клиентсеого сервера, используется полноценными клиентами.
    Возаращяет: UserDTO(id,platform_id,name).
    """
    platform_id = (await session.execute(select(PlatformORM.id).where(PlatformORM.platform_name == platform_name))).scalar()
    res = await session.execute(insert(UserORM).returning(UserORM.id).values(platform_id=platform_id, name=name))
    await session.commit()
    return UserDTO(id=res.scalar(), platform_id=platform_id, name=name)


async def bot_user_registration(session: AsyncSession, platform_name: str, name: str) -> ChatUsersDTO:
    """
    Регистрирует новго пользователя и саздаёт новый чат в который его добавляет.
    Возвращяет: ChatUsersDTO(user.id,chat.id).
    """
    platform_id = (await session.execute(select(PlatformORM.id).where(PlatformORM.platform_name == platform_name))).scalar()
    bot_id = (await session.execute(insert(UserORM).returning(UserORM.id).values(platform_id=platform_id, name=name))).scalar()
    chat_id = (await session.execute(insert(ChatORM).returning(ChatORM.id).values(name=name))).scalar()
    await session.execute(insert(WaitingСhatORM).values(chat_id=chat_id))
    await session.execute(insert(ChatUsersORM).values(user_id=bot_id, chat_id=chat_id))
    await session.commit()
    return ChatUsersDTO(user_id=bot_id, chat_id=chat_id)
