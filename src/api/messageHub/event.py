from src.api.messageHub.utils import send_http_request
from pydantic import BaseModel
from typing import Any

from src.database.schemes import *

from src.settings import settings

import uuid

class Event(BaseModel):
    name: str
    data: Any
    id: uuid.UUID

async def send_event(platforms: list[PlatformDTO], event: Event):
    """
    Отправка сообщения всем платформам
    """
    dict_event = event.model_dump(mode="json")
    for platform in platforms:
         await send_http_request(base_url=platform.url, relative_url=settings.END_POINT_EVENT,json=dict_event)


# Update chat
async def handler_update_chat(platforms: list[PlatformDTO], chat: ChatDTO, event_id: uuid.UUID):
    event = Event(
        name="chat.update",
        data={
            chat: chat
        },
        id=event_id
    )
    await send_event(platforms,event)

handlers_update_chat = [handler_update_chat]

async def call_handlers_update_chat(platforms: list[PlatformDTO], chat: ChatDTO, event_id: uuid.UUID = uuid.uuid4()):
    for item in handlers_update_chat:
        await item(platforms, chat, event_id)


# user_add_to_chat
async def handler_user_add_to_chat(platforms: list[PlatformDTO], chat: ChatDTO, user: UserDTO, event_id: uuid.UUID):
    event = Event(
        name="chat.add.user",
        data={
            chat: chat,
            user: user
        },
        id=event_id
    )
    await send_event(platforms,event)

handlers_user_add_to_chat = [handler_user_add_to_chat]

async def call_handlers_user_add_to_chat(platforms: list[PlatformDTO], chat: ChatDTO, user: UserDTO, event_id: uuid.UUID = uuid.uuid4()):
    for item in handlers_user_add_to_chat:
        await item(platforms, chat, user, event_id)


# set_last_read_message_id
async def handler_set_last_read_message_id(platforms: list[PlatformDTO], chat_id: int, user_id: int, last_read_message_id: int, event_id: uuid.UUID):
    event = Event(
        name="chat.set.last_read_message_id",
        data={
            chat_id: chat_id,
            user_id: user_id,
            last_read_message_id: last_read_message_id,
        },
        id=event_id
    )
    await send_event(platforms,event)

handlers_set_last_read_message_id = [handler_set_last_read_message_id]

async def call_handlers_set_last_read_message_id(platforms: list[PlatformDTO], chat_id: int, user_id: int, last_read_message_id: int, event_id: uuid.UUID = uuid.uuid4()):
    for item in handlers_set_last_read_message_id:
        await item(platforms, chat_id, user_id, last_read_message_id, event_id)


# send_messge_broadcast
async def handler_send_messge_broadcast(platforms: list[PlatformDTO], message: MessageDTO, event_id: uuid.UUID):
    event = Event(
        name="chat.new_message",
        data={
            message: message,
        },
        id=event_id
    )
    await send_event(platforms,event)

handlers_send_messge_broadcast = [handler_send_messge_broadcast]

async def call_handlers_send_messge_broadcast(platforms: list[PlatformDTO], message: MessageDTO, event_id: uuid.UUID = uuid.uuid4()):
    for item in handlers_send_messge_broadcast:
        await item(platforms, message, event_id)
