from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from ....settings import settings
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

import logging

logging.basicConfig(level=logging.INFO,
                    filename="py_log.log", filemode="w")

router = APIRouter()


class UserIn(BaseModel):
    platform_name: str = Field(max_length=30)
    name: str = Field(max_length=256)


@router.post("/user_registration/bot")
async def registr_bot_user(background_tasks: BackgroundTasks, user: UserIn, session: AsyncSession = Depends(get_session)):
    """
    Регистрирует пользователя из бота.
    """
    try:
        res = await bot_user_registration(session=session, platform_name=user.platform_name, name=user.name)
    except IntegrityError as err:
        logging.info(err)
        raise HTTPException(status_code=422, detail="platform_not_fund")

    platforms = await get_all_platform(session=session)
    chat = await get_chat_by_id(session=session, chat_id=res.chat_id)
    for platform in platforms:
        if platform.platform_type == "web":
            background_tasks.add_task(
                send_notification_added_waiting_chat, url=platform.url, chat=chat)
            # background_tasks.add_task(send_notification_added_waiting_chat,url="http://localhost:8001", chat=chat)

    return {"user_id": res.user_id, "chat_id": res.chat_id}


async def send_notification_added_waiting_chat(url: str, chat: ChatDTO):
    async with AsyncClient(base_url=url) as clinet:
        try:
            response = await clinet.post(settings.END_POINT_SEND_NOTIFICATION_ADDED_WAITING_CHAT, json={"id": chat.id, "name": chat.name})
            response.raise_for_status()
        except Exception as e:
            print(f"send_notification_added_waiting_chat Error: {e}")
            logging.error(f"Error: {e}")


@router.post("/user_registration/web")
async def registr_web_user(user: UserIn, session: AsyncSession = Depends(get_session)):
    """
    Регистрирует пользователя из web.
    """
    try:
        res = await user_registration(session=session, platform_name=user.platform_name, name=user.name)
    except IntegrityError as err:
        logging.info(err)
        raise HTTPException(status_code=422, detail="platform_not_fund")

    return {"user_id": res.id}
