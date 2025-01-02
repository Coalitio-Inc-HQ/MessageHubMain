from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from typing import Literal

from ....settings import settings

from pydantic import BaseModel

from src.loging.logging_utility import log, LogMessage,log_en
from src.api.messageHub.utils import send_http_request


from src.database.utilities import insert_data, update_data, select_data_arr, select_data_one_or_none, select_data_one_or_none_quer,select_data_arr_quer

from src.api.messageHub.event import call_handlers_update_chat, call_handlers_send_messge_broadcast

import uuid

router = APIRouter()


@router.post("/send_a_message_to_chat")
async def send_a_message_to_chat(background_tasks: BackgroundTasks, message: MessageDTO, event_id: uuid.UUID = Body(), session: AsyncSession = Depends(get_session)):
    """
    Отправляет сообщение в чат.
    """

    # Проверяем принадлежит ли пользователь отправивший сооющение к данному чату
    if (not await whether_the_user_is_in_the_chat(session=session, chat_id=message.chat_id, user_id=message.sender_id)):
        raise HTTPException(status_code=422, detail="Пользователь не находится в данном чате")

    res = await save_messege(session=session, message=message)

    platforms = await get_all_platform(session=session)

    chat = await select_data_one_or_none(session, ChatORM, ChatDTO, ChatORM.id==message.chat_id)
    old_chat_is_archive = chat.is_archive

    change_chat = False
    # Если чат был в архиве то необходимо вывести из архива
    if chat.is_archive:
        change_chat = True
        chat.is_archive = False

    # Проверка от кого пришло сообщение
    sub_quer = select(UserORM.platform_id).where(UserORM.id==message.sender_id).scalar_subquery()
    quer = select(PlatformORM).where(PlatformORM.id == sub_quer)
    user_platform = await select_data_one_or_none_quer(session, PlatformDTO, quer)
    if user_platform.platform_type != "bot":
        if chat.is_waiting_answer != False:
            # Если сообщение пришло от сотрудника чат больше не ожидающий
            change_chat = True
            chat.is_waiting_answer = False
    else:
        # Новое сообщение от клиента в архивном чате нужно указать ожидание ответа
        if old_chat_is_archive == True:
            change_chat = True
            chat.is_waiting_answer = True


    # Отправка события
    if change_chat:
        await update_data(session, ChatORM, ChatORM.id==chat.id, **(chat.model_dump()))
        background_tasks.add_task(call_handlers_update_chat, platforms=platforms, chat=chat)

    # if chat.is_waiting_answer:
    #     background_tasks.add_task(send_messge_broadcast, platforms=platforms, message=message)
    # else:
    #     background_tasks.add_task(send_messge_personal, platforms=platforms, message=message)

    # background_tasks.add_task(send_messge_broadcast, platforms=platforms, message=message)
    background_tasks.add_task(call_handlers_send_messge_broadcast, platforms=platforms, message=message, event_id=event_id)

    log(LogMessage(time=None,heder="Сообщение отправлено в чат.", heder_dict={"message":message},body=res,level=log_en.DEBUG))
    return {"message_id": res.id}


# async def send_messge_broadcast(platforms: list[PlatformDTO], message: MessageDTO):
#     """
#     Отправка сообщения всем платформам
#     """
#     dict_message = message.model_dump()
#     dict_message["sended_at"] = message.sended_at.isoformat()
#     for platform in platforms:
#          await send_http_request(base_url=platform.url, relative_url=settings.END_POINT_SEND_MESSAGE,json=dict_message)


# async def send_messge_personal(platforms: list[PlatformDTO], message: MessageDTO):
#     """
#     Отправка сообщения всем платформам
#     """
#     dict_message = message.model_dump()
#     dict_message["sended_at"] = message.sended_at.isoformat()
#     for platform in platforms:
#          await send_http_request(base_url=platform.url, relative_url=settings.END_POINT_SEND_PERSONAL_MESSAGE,json=dict_message)


@router.post("/get_messages_from_chat")
async def get_messges_from_chat_(chat_id: int = Body(), count: int = Body(), offset_message_id: int = Body(), include_messege: bool = Body(), mode: Literal["up","down"] = Body() , session: AsyncSession = Depends(get_session)):
    """
    Возвращает сообщения из чата.
    """
    if (count < 0):
        raise HTTPException(status_code=422, detail="count<0")

    if offset_message_id==-1:
        res = (await select_data_arr_quer(session, MessageDTO, select(MessageORM)
                                                                .where(MessageORM.chat_id == chat_id)
                                                                .order_by(MessageORM.sended_at.desc(), MessageORM.id.desc())
                                                                .limit(count))
                )[::-1]
    else:
        if mode == "up":
            if include_messege:
                res = (await select_data_arr_quer(session, MessageDTO, select(MessageORM)
                                                                        .where(MessageORM.chat_id == chat_id, MessageORM.id<=offset_message_id)
                                                                        .order_by(MessageORM.sended_at.desc(), MessageORM.id.desc())
                                                                        .limit(count))
                )[::-1]
            else:
                res = (await select_data_arr_quer(session, MessageDTO, select(MessageORM)
                                                                        .where(MessageORM.chat_id == chat_id, MessageORM.id<offset_message_id)
                                                                        .order_by(MessageORM.sended_at.desc(), MessageORM.id.desc())
                                                                        .limit(count))
                )[::-1]
        else:
            if include_messege:
                res = await select_data_arr_quer(session, MessageDTO, select(MessageORM)
                                                        .where(MessageORM.chat_id == chat_id, MessageORM.id>=offset_message_id)
                                                        .order_by(MessageORM.sended_at.asc(), MessageORM.id.asc())
                                                        .limit(count))
            else:
                res = await select_data_arr_quer(session, MessageDTO, select(MessageORM)
                                        .where(MessageORM.chat_id == chat_id, MessageORM.id>offset_message_id)
                                        .order_by(MessageORM.sended_at.asc(), MessageORM.id.asc())
                                        .limit(count))

    log(LogMessage(time=None,heder="Получены сообщения из чата.", heder_dict={"chat_id":chat_id, "count":count, "offset_message_id":offset_message_id},body=res,level=log_en.DEBUG))

    return res
