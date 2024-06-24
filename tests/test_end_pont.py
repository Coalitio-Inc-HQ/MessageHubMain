from httpx import AsyncClient
from conftest import async_session_maker
from src.database.database_requests import *
import datetime


async def test_platform_registration_bot(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bot", json={"platform_name": "telegram", "url": "https://tele_bot"})
    assert response.status_code == 200


async def test_user_registration_bot(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вова"})
    assert response.status_code == 200


async def test_send_a_message_to_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers = response1.json()
    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    assert response.status_code == 200


def date_time_convert(t: datetime.datetime) -> str:
    return f"{t.year:04}-{t.month:02}-{t.day:02}T{t.hour:02}:{t.minute:02}:{t.second:02}.{t.microsecond:03}Z"
