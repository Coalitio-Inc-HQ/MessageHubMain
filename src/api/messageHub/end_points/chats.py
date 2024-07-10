from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from ....settings import settings

from pydantic import BaseModel

import logging

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/get_list_of_waiting_chats")
async def get_waiting_chats(count: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Отдаёт список всех ожидающих чатов.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    res = await get_list_of_waiting_chats(session=session, count=count)
    return res


@router.post("/get_chats_by_user")
async def get_chats_by_user_(user_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает чаты пользователя.
    """
    # Надо ли проверять существование пользователя?
    res = await get_chats_by_user_id(session=session, user_id=user_id)
    return res


@router.post("/get_users_by_chat_id")
async def get_users_by_chat_id_(user_id: int = Body(), chat_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает участников чата.
    """
    # Проверяем принадлежность пользователя к чату
    if (not await whether_the_user_is_in_the_chat(session=session, chat_id=chat_id, user_id=user_id) and not await is_waiting_chat(session=session, chat_id=chat_id)):
        raise HTTPException(
            status_code=422, detail="Пользователь не находится в данном чате")
    
    res = await get_users_by_chat_id(session=session, chat_id=chat_id)
    return res


@router.post("/connect_to_a_waiting_chat")
async def connect_to_waiting_chat(background_tasks: BackgroundTasks, user_id: int = Body(), chat_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Подключает к ожидающему чату.
    """
    try:
        res = await connect_to_a_waiting_chat(session=session, user_id=user_id, chat_id=chat_id)
    except IntegrityError as err:
        raise HTTPException(
            status_code=422, detail="Ползователь уже находится в чате")

    # получаем нужную информацию для оповещения
    chat = await get_chat_by_id(session=session, chat_id=chat_id)
    platforms = await get_all_platform(session=session)

    # оповещяем что чат больше не является ожидающим
    background_tasks.add_task(
        send_notifications_deleted_waiting_chat, platforms=platforms, chat=chat)

    """
    Нужночто-то сделать с платформами !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
    И убрать дублирование с connect_to_chat
    """
    user = await get_user_by_user_id(session=session, user_id=user_id)

    platforms = await get_platforms_by_chat_id(session=session, chat_id=chat_id)

    # проверяем присудствует ли платформа добовляемого пользователя в списке
    is_fund_platform = False
    for platf in platforms:
        if platf.id == user.platform_id:
            is_fund_platform = True
            break

    if not is_fund_platform:
        platforms.append(platform=await get_platform_by_user_id(session=session, user_id=user_id))

    # оповещяем платформу о том, что в чат был добавленн новый пользователь
    await send_notifications_user_added_to_chat(platforms=platforms, user=user, chat=chat)

    return res


async def send_notifications_deleted_waiting_chat(platforms: list[PlatformDTO], chat: ChatDTO):
    """
    Отправка сообщений всем платформам о том, что чат больше не является ожидающим
    """
    for platform in platforms:
        if not platform.platform_type == "bot":
            await send_notification_deleted_waiting_chat(url=platform.url, chat=chat)


async def send_notification_deleted_waiting_chat(url: str, chat: ChatDTO):
    """
    Отправка сообщения о том что, чат больше не является ожидающим
    """
    async with AsyncClient(base_url=url) as clinet:
        try:
            response = await clinet.post(settings.END_POINT_SEND_NOTIFICATION_DELITED_WAITING_CHAT, json=chat.model_dump())
            response.raise_for_status()
        except Exception as e:
            print(
                f"Ошибка отправки сообщения о том, что чат больше не является ожидающим: {e}")
            logger.error(f"Error: {e}")


@router.post("/connect_user_to_chat")
async def connect_user_to_chat_(background_tasks: BackgroundTasks, user_id: int = Body(), chat_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Подключает к ожидающему чату.
    """
    try:
        res = await connect_user_to_chat(session=session, user_id=user_id, chat_id=chat_id)
    except IntegrityError as err:
        raise HTTPException(
            status_code=422, detail="Ползователь уже находится в чате")

    # получаем нужную информацию для оповещения
    chat = await get_chat_by_id(session=session, chat_id=chat_id)
    user = await get_user_by_user_id(session=session, user_id=user_id)

    platforms = await get_platforms_by_chat_id(session=session, chat_id=chat_id)

    # проверяем присудствует ли платформа добовляемого пользователя в списке
    is_fund_platform = False
    for platf in platforms:
        if platf.id == user.platform_id:
            is_fund_platform = True
            break

    if not is_fund_platform:
        platforms.append(platform=await get_platform_by_user_id(session=session, user_id=user_id))

    # оповещяем платформу о том, что в чат был добавленн новый пользователь
    await send_notifications_user_added_to_chat(platforms=platforms, user=user, chat=chat)

    return res


async def send_notifications_user_added_to_chat(platforms: list[PlatformDTO], user: UserDTO, chat: ChatDTO):
    """
    Отправка сообщений всем платформам о том, что пользователь добавлен в чат
    """
    for platform in platforms:
        if not platform.platform_type == "bot":
            await send_notification_user_added_to_chat(url=platform.url, user=user, chat=chat)


async def send_notification_user_added_to_chat(url: str, user: UserDTO, chat: ChatDTO):
    """
    Отправка сообщения о том, что в чат был добавленн новый пользователь
    """
    async with AsyncClient(base_url=url) as clinet:
        try:
            response = await clinet.post(settings.END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT, json={"user": user.model_dump(), "chat": chat.model_dump()})
            response.raise_for_status()
        except Exception as e:
            print(
                f"Ошибка отправки сообщения о том, что в чат был добавленн новый пользователь: {e}")
            logger.error(f"Error: {e}")
