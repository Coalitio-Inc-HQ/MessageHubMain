from fastapi import APIRouter, Body, Depends, HTTPException
from ..database.session_database import get_session, AsyncSession
from ..database.database_requests import *
from httpx import AsyncClient
from typing import Union

from ..settings import settings

router = APIRouter(prefix="/message_service")


@router.post("/platform_registration/{platform_type}")
async def registr_platform(platform_type: str, platform_name: str = Body(), url: str = Body(), session: AsyncSession = Depends(get_session)):
    """
    Регестрирует платформу бота.
    """
    if len(platform_type) > 3:
        raise HTTPException(status_code=422, detail="len(platform_type)>3")
    platforms = await get_platforms_by_name(session=session, platform_name=platform_name)
    if not len(platforms) == 0:
        await update_platforms_by_name(session=session, platform_name=platform_name, url=url)
        return {"status": "ok"}
    else:
        await platform_registration(session=session, platform_type=platform_type, platform_name=platform_name, url=url)
        return {"status": "ok"}


@router.post("/user_registration/bot")
async def registr_bot_user(platform_name: str = Body(), name: str = Body(), session: AsyncSession = Depends(get_session)):
    """
    Регестрирует пользователя из бота.
    """
    # обработка добавлеения чата в ожидание!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res = await bot_user_registration(session=session, platform_name=platform_name, name=name)
    return {"user_id": res.user_id, "chat_id": res.chat_id}


@router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(message: MessageDTO, session: AsyncSession = Depends(get_session)):
    """
    Отправляет сообщение в чат.
    """
    res = await save_messege(session=session, message=message)
    platforms = await get_platforms_by_chat_id(session=session, chat_id=message.chat_id)
    for platform in platforms:
        send_messge(platform.url, message)
        # await send_messge("http://localhost:8000/message_service",message)
    return {"status": "ok"}


async def send_messge(url: str, message: MessageDTO):
    async with AsyncClient(base_url=url) as clinet:
        try:
            response = await clinet.post(settings.END_POINT_SEND_MESSAGE, json={"id": message.id, "chat_id": message.chat_id, "sender_id": message.sender_id, "sended_at": date_time_convert(message.sended_at), "text": message.text})
            response.raise_for_status()
        except Exception as e:
            print(f"Error: {e}")


def date_time_convert(t: datetime.datetime) -> str:
    return f"{t.year:04}-{t.month:02}-{t.day:02}T{t.hour:02}:{t.minute:02}:{t.second:02}.{t.microsecond:03}Z"


@router.post("/user_registration/web")
async def registr_bot_user(platform_name: str = Body(), name: str = Body(), session: AsyncSession = Depends(get_session)):
    """
    Регестрирует пользователя из web.
    """
    res = await user_registration(session=session, platform_name=platform_name, name=name)
    return {"user_id": res.id}


@router.post("/get_list_of_waiting_chats")
async def get_waiting_chats(count: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Отдаёт список всех ожидающих чатов.
    """
    res = await get_list_of_waiting_chats(session=session,count=count)
    return res


@router.post("/connect_to_a_waiting_chat")
async def connect_to_waiting_chat(user_id: int = Body(),chat_id:int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Подключает к ожидающему чату.
    """
    # оповещение о добавлении к чату !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res = await connect_to_a_waiting_chat(session=session,user_id = user_id,chat_id=chat_id)
    return res


@router.post("/connect_user_to_chat")
async def connect_user_to_chat_(user_id: int = Body(),chat_id:int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Подключает к ожидающему чату.
    """
    # оповещение о добавлении к чату !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res = await connect_user_to_chat(session=session,user_id = user_id,chat_id=chat_id)
    return res


@router.post("/get_chats_by_user")
async def get_chats_by_user_(user_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращяет чаты пользователя.
    """
    res = await get_chats_by_user_id(session=session,user_id = user_id)
    return res


@router.post("/get_messges_from_chat")
async def get_messges_from_chat_(chat_id: int = Body(),count: int =Body(),offset_message_id:int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращяет сообщения из чата.
    """
    res = await get_messges_from_chat(session=session,chat_id=chat_id,count=count,offset_message_id=offset_message_id)
    return res
