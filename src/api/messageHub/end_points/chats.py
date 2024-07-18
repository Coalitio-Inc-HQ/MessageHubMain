from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from ....database.session_database import get_session, AsyncSession
from ....database.database_requests import *
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from ....settings import settings

from src.api.messageHub.utils import send_http_request
from src.loging.logging_utility import log, LogMessage,log_en

router = APIRouter()

@router.post("/get_chats_in_which_user_is_not_member")
async def get_waiting_chats(user_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Отдаёт список всех чатов в которых не состоит пользователь.
    """
    res = await get_list_of_chats_in_which_user_is_not_member(session=session, user_id=user_id)
    log(LogMessage(time=None,heder="Получен список чатов в которых не состоит пользователь.", heder_dict={"user_id":user_id},body=res,level=log_en.DEBUG))
    return res


@router.post("/get_chats_by_user")
async def get_chats_by_user_(user_id: int = Body(), session: AsyncSession = Depends(get_session)):
    """
    Возвращает чаты пользователя.
    """
    # Надо ли проверять существование пользователя?
    res = await get_chats_by_user_id(session=session, user_id=user_id)
    log(LogMessage(time=None,heder="Получен список чатов пользователя.", heder_dict={"user_id":user_id},body=res,level=log_en.DEBUG))
    return res


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
    try:
        res = await connect_user_to_chat(session=session, user_id=user_id, chat_id=chat_id)
    except IntegrityError as err:
        raise HTTPException(
            status_code=422, detail="Ползователь уже находится в чате")

    # получаем нужную информацию для оповещения
    chat = await get_chat_by_id(session=session, chat_id=chat_id)
    user = await get_user_by_user_id(session=session, user_id=user_id)

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


async def send_notifications_user_added_to_chat(platforms: list[PlatformDTO], user: UserDTO, chat: ChatDTO):
    """
    Отправка сообщений всем платформам о том, что пользователь добавлен в чат
    """
    for platform in platforms:
        if not platform.platform_type == "bot":
            await send_http_request(base_url=platform.url,relative_url=settings.END_POINT_SEND_NOTIFICATION_USER_ADDED_TO_CHAT, json={"user": user.model_dump(), "chat": chat.model_dump()})