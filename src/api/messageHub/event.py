from src.api.messageHub.utils import send_http_request
from pydantic import BaseModel
from typing import Any

from src.database.schemes import *

from src.settings import settings

class Event(BaseModel):
    name: str
    data: Any

async def send_event(platforms: list[PlatformDTO], event: Event):
    """
    Отправка сообщения всем платформам
    """
    dict_event = event.model_dump(mode="json")
    for platform in platforms:
         await send_http_request(base_url=platform.url, relative_url=settings.END_POINT_EVENT,json=dict_event)


# Update chat
async def handler_update_chat(platforms: list[PlatformDTO], chat: ChatDTO):
    event = Event(
        name="chat.update",
        data=chat
    )
    await send_event(platforms,event)

handlers_update_chat = [handler_update_chat]

async def call_handlers_update_chat(platforms: list[PlatformDTO], chat: ChatDTO):
    for item in handlers_update_chat:
        await item(platforms, chat)