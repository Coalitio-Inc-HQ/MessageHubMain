from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from ....settings import settings
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from src.loging.logging_utility import log, LogMessage,log_en
from src.api.messageHub.utils import send_http_request

import logging

router = APIRouter()


class UserIn(BaseModel):
    """
    Модель входных данных для регистрации пользователя
    """
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
        log(LogMessage(time=None,heder="Платформа не найдена.", 
                   heder_dict=err.args,body=
                    {
                        "user":user
                    },
                    level=log_en.ERROR))
        raise HTTPException(status_code=422, detail="Платформа не найдена")

    # получаем мнформацию для оповещения платформ
    platforms = await get_all_platform(session=session)
    chat = await get_chat_by_id(session=session, chat_id=res.chat_id)

    # Оповещяем о добавлении ожидающего чата
    background_tasks.add_task(
        send_notifications_added_waiting_chat, platforms=platforms, chat=chat)

    return {"user_id": res.user_id, "chat_id": res.chat_id}


async def send_notifications_added_waiting_chat(platforms: list[PlatformDTO], chat: ChatDTO):
    """
    Оповещение платформ о добавлении ожидающего чата
    """
    for platform in platforms:
        if not platform.platform_type == "bot":
            await send_http_request(base_url=platform.url,relative_url=settings.END_POINT_SEND_NOTIFICATION_ADDED_WAITING_CHAT,json=chat.model_dump())


@router.post("/user_registration/web")
async def registr_web_user(user: UserIn, session: AsyncSession = Depends(get_session)):
    """
    Регистрирует пользователя из web.
    """
    try:
        res = await user_registration(session=session, platform_name=user.platform_name, name=user.name)
    except IntegrityError as err:
        log(LogMessage(time=None,heder="Платформа не найдена.", 
                   heder_dict=err.args,body=
                    {
                        "user":user
                    },
                    level=log_en.ERROR))
        raise HTTPException(status_code=422, detail="Платформа не найдена")

    return {"user_id": res.id}
