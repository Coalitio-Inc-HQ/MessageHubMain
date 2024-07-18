from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from ....settings import settings

from pydantic import BaseModel

from src.loging.logging_utility import log, LogMessage,log_en
from src.api.messageHub.utils import send_http_request


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

    platforms = await get_all_platform(session=session)
    background_tasks.add_task(
        send_messge_broadcast, platforms=platforms, message=message)
    
    log(LogMessage(time=None,heder="Сообщение отправлено в чат.", heder_dict={"message":message},body=res,level=log_en.DEBUG))
    return {"message_id": res.id}


async def send_messge_broadcast(platforms: list[PlatformDTO], message: MessageDTO):
    """
    Отправка сообщения всем платформам
    """
    dict_message = message.model_dump()
    dict_message["sended_at"] = message.sended_at.isoformat()
    for platform in platforms:
         await send_http_request(base_url=platform.url, relative_url=settings.END_POINT_SEND_MESSAGE,json=dict_message)


@router.post("/get_messages_from_chat")
async def get_messges_from_chat_(chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из чата.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    res = await get_messges_from_chat(session=session, chat_id=chat_id, count=count, offset_message_id=offset_message_id)
    log(LogMessage(time=None,heder="Получены сообщения из чата.", heder_dict={"chat_id":chat_id, "count":count, "offset_message_id":offset_message_id},body=res,level=log_en.DEBUG))
    return res
