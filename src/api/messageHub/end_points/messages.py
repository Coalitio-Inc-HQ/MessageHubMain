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
        platforms = await get_all_platform(session=session)
        background_tasks.add_task(
            send_messge_broadcast, platforms=platforms, message=message)
    else:
        platforms = await get_platforms_by_chat_id(session=session, chat_id=message.chat_id)
        background_tasks.add_task(
            send_messge_normal, platforms=platforms, message=message)

    return {"message_id": res.id}


async def send_messge_normal(platforms: list[PlatformDTO], message: MessageDTO):
    """
    Отправка сообщения платформам
    """
    for platform in platforms:
        await send_message(platform, message, settings.END_POINT_SEND_MESSAGE)


async def send_messge_broadcast(platforms: list[PlatformDTO], message: MessageDTO):
    """
    Отправка сообщения из ожидающего чата всем платформам
    """
    for platform in platforms:
        if not platform.platform_type == "bot":
            await send_message(platform, message,settings.END_POINT_SEND_MESSAGE_BROADCAST )


async def send_message(platform: PlatformDTO,  message: MessageDTO, ur:str):
    """
    Отправка сообщения платформе
    """
    async with AsyncClient(base_url=platform.url) as clinet:
                try:
                    dict_message = message.model_dump()
                    dict_message["sended_at"] = message.sended_at.isoformat()
                    response = await clinet.post(ur, json=dict_message)
                    response.raise_for_status()
                except Exception as err:
                    print(
                        f"Ошибка отправки сообщения из ожидающего чата Error: {err}")
                    logger.error(f"Error: {err}")
    

@router.post("/get_messages_from_chat")
async def get_messges_from_chat_(user_id: int = Body(), chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из чата.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    # Проверяем принадлежит ли пользователь чату
    if (not await whether_the_user_is_in_the_chat(session=session, chat_id=chat_id, user_id=user_id)):
        raise HTTPException(
            status_code=422, detail="Пользователь не находится в данном чате")

    res = await get_messges_from_chat(session=session, chat_id=chat_id, count=count, offset_message_id=offset_message_id)
    return res


@router.post("/get_messages_from_wating_chat")
async def get_messges_from_chat_(chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из ожидающего чата.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    # Проверяем является ли чат ожидающим
    if not await is_waiting_chat(session=session, chat_id=chat_id):
        raise HTTPException(
            status_code=422, detail="Чат не является ожидающим")

    res = await get_messges_from_chat(session=session, chat_id=chat_id, count=count, offset_message_id=offset_message_id)
    return res
