from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from ....settings import settings

from src.api.messageHub.utils import send_http_request
from src.loging.logging_utility import log, LogMessage,log_en

from src.database.schemes_temp import *

from src.database.utilities import insert_data, update_data, select_data_arr, select_data_one_or_none, select_data_one_or_none_quer,select_data_arr_quer

from sqlalchemy import or_

from src.api.messageHub.event import call_handlers_update_chat

router = APIRouter()


@router.post("/get_chats")
async def get_chats(user_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает чаты пользователя.
    """
    
    chats = await select_data_arr_quer(session, ExtChatDTO, select(ChatORM,ChatUsersORM).join(ChatUsersORM).where(ChatUsersORM.user_id==user_id))

    subqer = select(ChatUsersORM.chat_id).where(ChatUsersORM.user_id==user_id)
    # unconn_chats = await select_data_arr_quer(session,ExtChatDTO,select(ChatORM).where(ChatORM.id.not_in(subqer), ChatORM.is_waiting_answer == True))
    unconn_chats = await select_data_arr_quer(session,ExtChatDTO,select(ChatORM).where(ChatORM.id.not_in(subqer)))
    chats = chats + unconn_chats

    return chats


@router.post("/get_users_by_chat_id")
async def get_users_by_chat_id_(chat_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает участников чата.
    """
    res = await get_users_by_chat_id(session=session, chat_id=chat_id)
    log(LogMessage(time=None,heder="Получен список пользователей чата.", heder_dict={"chat_id":chat_id},body=res,level=log_en.DEBUG))
    return res

@router.post("/connect_user_to_chat")
async def connect_user_to_chat_(background_tasks: BackgroundTasks, user_id: int = Body(), chat_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Подключает к чату.
    """
    res = await select_data_one_or_none(session, ChatUsersORM, ChatUsersDTO, ChatUsersORM.chat_id == chat_id, ChatUsersORM.user_id == user_id)

    if res and res.user_in_chat:
        raise HTTPException(status_code=422, detail="Ползователь уже находится в чате")

    if res:
        await update_data(session, ChatUsersORM, ChatUsersORM.chat_id == chat_id, ChatUsersORM.user_id == user_id, user_in_chat=True)
        res.user_in_chat=True
    else:
        await insert_data(session, ChatUsersORM,
                          data={
                                "chat_id":chat_id,
                                "user_id":user_id,
                                "user_in_chat":True,
                                }
                          )
        res = ChatUsersDTO(user_id=user_id,chat_id=chat_id,user_in_chat=True)

    # получаем нужную информацию для оповещения
    chat = await get_chat_by_id(session=session, chat_id=chat_id)

    user = await get_user_by_user_id(session=session, user_id=user_id)

    # Выбрать все платформы
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
    background_tasks.add_task(send_notifications_user_added_to_chat,platforms=platforms, user=user, chat=chat)

    log(LogMessage(time=None,heder="Пользователь добавлен в чат.", heder_dict={"chat_id":chat_id, "user_id":user_id},body={"chat":chat,"user":user},level=log_en.DEBUG))
    
    return res


async def send_notifications_user_added_to_chat(platforms: list[PlatformDTO], user: UserDTO, chat: ChatDTO_TEMP):
    """
    Отправка сообщений всем платформам о том, что пользователь добавлен в чат
    """
    for platform in platforms:
        if not platform.platform_type == "bot":
            await send_http_request(base_url=platform.url,relative_url=settings.END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT, json={"user": user.model_dump(), "chat": chat.model_dump()})



@router.post("/remove_to_archive")
async def remove_to_archive_(background_tasks: BackgroundTasks, chat_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Уберает чат в архив.
    """
    sunq = select(UserORM.id).where(
        UserORM.platform_id.not_in(
            select(PlatformORM.id).where(PlatformORM.platform_type=="bot")
        )
    )
    await update_data(session, ChatUsersORM,ChatUsersORM.chat_id==chat_id,ChatUsersORM.user_id.in_(sunq),user_in_chat=False)
    await update_data(session, ChatORM, ChatORM.id==chat_id, is_archive=True)

    chat = await select_data_one_or_none(session, ChatORM, ChatDTO, ChatORM.id==chat_id)
    platforms = await get_all_platform(session=session)
    background_tasks.add_task(call_handlers_update_chat, platforms=platforms, chat=chat)