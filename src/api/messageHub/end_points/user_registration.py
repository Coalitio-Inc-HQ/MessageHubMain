from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from ....settings import settings
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from src.loging.logging_utility import log, LogMessage,log_en
from src.api.messageHub.utils import send_http_request

from src.database.schemes_temp import *

import logging

from src.database.utilities import insert_data, update_data, select_data_arr, select_data_one_or_none, select_data_one_or_none_quer,select_data_arr_quer

from src.api.messageHub.event import call_handlers_update_chat


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

    # Оповещяем о добавлении чата
    background_tasks.add_task(call_handlers_update_chat, platforms=platforms, chat=chat)

    log(LogMessage(time=None,heder="Зарегистрирован пользователь из бота.", heder_dict=user,body={"user":user,"chat":chat},level=log_en.DEBUG))
    return {"user_id": res.user_id, "chat_id": res.chat_id}


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

    log(LogMessage(time=None,heder="Зарегистрирован пользователь из web.", heder_dict=user,body={"user":res},level=log_en.DEBUG))
    return {"user_id": res.id}


@router.post("/employees")
async def get_employees(session: AsyncSession = Depends(get_session)):
    """
    Получает сотрудников организации
    """

    employees = await select_data_arr_quer(session,UserDTO,select(UserORM).join(PlatformORM).where(PlatformORM.platform_name=="web"))
    return employees