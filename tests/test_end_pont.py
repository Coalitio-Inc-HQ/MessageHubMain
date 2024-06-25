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


async def test_platform_registration_web(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/web", json={"platform_name": "web", "url": "https://web"})
    assert response.status_code == 200


async def test_user_registration_web(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa"})
    assert response.status_code == 200


async def test_get_list_of_waiting_chats(ac: AsyncClient):
    response = await ac.post("/message_service/get_list_of_waiting_chats", json='-1')
    assert response.status_code == 200


async def test_connect_to_a_waiting_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa"})

    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id":chatusers2["user_id"],"chat_id":chatusers1["chat_id"]})
    assert response.status_code == 200


async def test_connect_user_to_chat_(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa"})

    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_user_to_chat", json={"user_id":chatusers2["user_id"],"chat_id":chatusers1["chat_id"]})
    assert response.status_code == 200


async def test_get_chats_by_user(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    response = await ac.post("/message_service/get_chats_by_user", json=chatusers1["user_id"])
    assert response.status_code == 200


async def test_send_a_message_to_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers = response1.json()
    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    
    mesg= response.json()

    response1 = await ac.post("/message_service/get_messges_from_chat", json={"chat_id": chatusers['user_id'], "count": 10,"offset_message_id":-1})

    assert response1.status_code == 200
