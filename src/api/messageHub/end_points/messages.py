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


@router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(background_tasks: BackgroundTasks, message: MessageDTO, session: AsyncSession = Depends(get_session)):
    """
    Отправляет сообщение в чат.
    """
    # Проверяем принадлежит ли пользователь отправивший сооющение к данному чату
    if (not await whether_the_user_is_in_the_chat(session=session, chat_id=message.chat_id, user_id=message.sender_id)):
        raise HTTPException(
            status_code=422, detail="Пользователь не находится в данном чате")

    res = await save_messege(session=session, message=message)

    # проверяем из ожидающего ли чата сообщение
    wating_hats = await get_list_of_waiting_chats(session=session, count=-1)
    is_wating_chat = False
    for chat in wating_hats:
        if chat.id == message.chat_id:
            is_wating_chat = True
            break

    if is_wating_chat:
        background_tasks.add_task(
            send_messge_broadcast, session=session, message=message)
    else:
        background_tasks.add_task(
            send_messge, session=session, message=message)

    return {"status": "ok"}


async def send_messge(session: AsyncSession, message: MessageDTO):
    """
    Отправка сообщения платформам
    """
    platforms = await get_platforms_by_chat_id(session=session, chat_id=message.chat_id)
    for platform in platforms:

        async with AsyncClient(base_url=platform.url) as clinet:
            try:
                response = await clinet.post(settings.END_POINT_SEND_MESSAGE, json={"id": message.id, "chat_id": message.chat_id, "sender_id": message.sender_id, "sended_at": date_time_convert(message.sended_at), "text": message.text})
                response.raise_for_status()
            except Exception as err:
                print(f"Ошибка отправки сообщения Error: {err}")
                logger.error(f"Error: {err}")


async def send_messge_broadcast(session: AsyncSession, message: MessageDTO):
    """
    Отправка сообщения из ожидающего чата всем платформам
    """
    platforms = await get_all_platform(session=session)
    for platform in platforms:
        if not platform.platform_type == "bot":
            async with AsyncClient(base_url=platform.url) as clinet:
                try:
                    response = await clinet.post(settings.END_POINT_SEND_MESSAGE_BROADCAST, json={"id": message.id, "chat_id": message.chat_id, "sender_id": message.sender_id, "sended_at": date_time_convert(message.sended_at), "text": message.text})
                    response.raise_for_status()
                except Exception as err:
                    print(f"Ошибка отправки сообщения из ожидающего чата Error: {err}")
                    logger.error(f"Error: {err}")


def date_time_convert(t: datetime.datetime) -> str:
    """
    Приведение даты-время к стандартному формату
    """
    return f"{t.year:04}-{t.month:02}-{t.day:02}T{t.hour:02}:{t.minute:02}:{t.second:02}.{t.microsecond:03}Z"


@router.post("/get_messages_from_chat")
async def get_messges_from_chat_(user_id: int = Body(), chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из чата.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    # Добавить проверку принадлежности к чату
    if (not await whether_the_user_is_in_the_chat(session=session, chat_id=chat_id, user_id=user_id)):
        raise HTTPException(
            status_code=422, detail="Пользователь не находится в данном чате")

    res = await get_messges_from_chat(session=session, chat_id=chat_id, count=count, offset_message_id=offset_message_id)
    return res


@router.post("/get_messages_from__wating_chat")
async def get_messges_from_chat_(chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из ожидающего чата.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    # Добавить проверку принадлежности к чату
    if not await is_waiting_chat(session=session,chat_id=chat_id):
        raise HTTPException(
            status_code=422, detail="Чат не является ожидающим")

    res = await get_messges_from_chat(session=session, chat_id=chat_id, count=count, offset_message_id=offset_message_id)
    return res
