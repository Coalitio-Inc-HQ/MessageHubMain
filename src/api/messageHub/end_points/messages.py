from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from ....settings import settings

from pydantic import BaseModel

import logging

logging.basicConfig(level=logging.INFO,
                    filename="py_log.log", filemode="w")

router = APIRouter()


@router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(background_tasks: BackgroundTasks,message: MessageDTO, session: AsyncSession = Depends(get_session)):
    """
    Отправляет сообщение в чат.
    """
    if (not await whether_the_user_is_in_the_chat(session=session,chat_id=message.chat_id,user_id=message.sender_id)):
        raise HTTPException(status_code=422,detail="Пользователь не находится в данном чате")
    res = await save_messege(session=session, message=message)
    platforms = await get_platforms_by_chat_id(session=session, chat_id=message.chat_id)
    for platform in platforms:
        background_tasks.add_task(send_messge,url= platform.url,message= message)
        # background_tasks.add_task(send_messge,url= "http://localhost:8001",message= message)
    return {"status": "ok"}


async def send_messge(url: str, message: MessageDTO):
    async with AsyncClient(base_url=url) as clinet:
        try:
            response = await clinet.post(settings.END_POINT_SEND_MESSAGE, json={"id": message.id, "chat_id": message.chat_id, "sender_id": message.sender_id, "sended_at": date_time_convert(message.sended_at), "text": message.text})
            response.raise_for_status()
        except Exception as e:
            print(f"send_messge Error: {e}")
            logging.error(f"Error: {e}")


def date_time_convert(t: datetime.datetime) -> str:
    return f"{t.year:04}-{t.month:02}-{t.day:02}T{t.hour:02}:{t.minute:02}:{t.second:02}.{t.microsecond:03}Z"


@router.post("/get_messages_from_chat")
async def get_messges_from_chat_(chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из чата.
    """
    if(count<0):
        raise HTTPException(status_code=422,detail="count<0")
    # if (not await whether_the_user_is_in_the_chat(session=session,chat_id=message.chat_id,user_id=message.sender_id)): !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #     raise HTTPException(status_code=422,detail="Пользователь не находится в данном чате")
    res = await get_messges_from_chat(session=session, chat_id=chat_id, count=count, offset_message_id=offset_message_id)
    return res
