from httpx import AsyncClient
from conftest import async_session_maker
from src.database.database_requests import *
import datetime


async def test_platform_registration_ok(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bot", json={"platform_name": "telegram", "url": "http://localhost:8001"})
    assert response.status_code == 200


async def test_platform_registration_type(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bots", json={"platform_name": "telegram", "url": "http://localhost:8001"})
    assert response.status_code == 422


async def test_platform_registration_name_30(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bot", json={"platform_name": "1234567890123456789012345678901", "url": "http://localhost:8001"})
    assert response.status_code == 422


async def test_platform_registration_url_256(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bot", json={"platform_name": "Test", "url": "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"})
    assert response.status_code == 422


async def test_user_registration_bot_ok(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вова"})
    assert response.status_code == 200


async def test_user_registration_bot_platform_name_30(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": "1234567890123456789012345678901", "name": "Вова"})
    assert response.status_code == 422


async def test_user_registration_bot_name_256(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"})
    assert response.status_code == 422


async def test_user_registration_bot_platform_not_found(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": "not_fund", "name": "Вова"})
    assert response.status_code == 422


async def test_platform_registration_web_ok(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/web", json={"platform_name": "web", "url": "http://localhost:8001"})
    assert response.status_code == 200


async def test_user_registration_web_ok(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa"})
    assert response.status_code == 200


async def test_user_registration_web_platform_name_30(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": "1234567890123456789012345678901", "name": "AAAaaaa"})
    assert response.status_code == 422


async def test_user_registration_web_name_256(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"})
    assert response.status_code == 422


async def test_user_registration_web_platform_not_fund(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": "web1", "name": "AAAaaaa"})
    assert response.status_code == 422


async def test_get_list_of_waiting_chats_ok(ac: AsyncClient):
    response = await ac.post("/message_service/get_list_of_waiting_chats", json='10')
    assert response.status_code == 200


async def test_get_list_of_waiting_chats_count(ac: AsyncClient):
    response = await ac.post("/message_service/get_list_of_waiting_chats", json='-1')
    assert response.status_code == 422


async def test_get_chats_by_user_ok(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    response = await ac.post("/message_service/get_chats_by_user", json=chatusers1["user_id"])
    assert response.status_code == 200


async def test_get_chats_by_user_user_not_found(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    response = await ac.post("/message_service/get_chats_by_user", json=chatusers1["user_id"])
    assert response.status_code == 200


async def test_get_users_by_chat_id_ok1(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa"})
    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": chatusers2["user_id"], "chat_id": chatusers1["chat_id"]})

    users = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": chatusers1["user_id"], "chat_id":chatusers1["chat_id"]})

    assert users.status_code == 200


async def test_get_users_by_chat_id_ok2(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася"})
    chatusers1 = response1.json()

    users = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": "-1", "chat_id":chatusers1["chat_id"]})

    assert users.status_code == 200


async def test_get_users_by_chat_id_chat_not_found(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася1"})
    chatusers1 = response1.json()

    response = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": chatusers1["user_id"], "chat_id": "-1"})

    assert response.status_code == 422


async def test_get_users_by_chat_id_user_not_found(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася2"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa2"})
    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": chatusers2["user_id"], "chat_id": chatusers1["chat_id"]})

    users = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": "-1", "chat_id":chatusers1["chat_id"]})

    assert users.status_code == 422


async def test_connect_to_a_waiting_chat_ok(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася13"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa13"})
    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": chatusers2["user_id"], "chat_id": chatusers1["chat_id"]})
    assert response.status_code == 200


async def test_connect_to_a_waiting_chat_already_in_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася12"})
    chatusers1 = response1.json()

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": chatusers1["user_id"], "chat_id": chatusers1["chat_id"]})
    assert response.status_code == 422


async def test_connect_user_to_chat_ok(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася11"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa11"})
    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_user_to_chat", json={"user_id": chatusers2["user_id"], "chat_id": chatusers1["chat_id"]})
    assert response.status_code == 200


async def test_connect_user_to_chat_already_in_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася0"})
    chatusers1 = response1.json()

    response = await ac.post("/message_service/connect_user_to_chat", json={"user_id": chatusers1["user_id"], "chat_id": chatusers1["chat_id"]})
    assert response.status_code == 422


async def test_send_a_message_to_chat_ok(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася9"})
    chatusers = response1.json()
    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    assert response.status_code == 200


async def test_send_a_message_to_chat_not_fund_user_in_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася8"})
    chatusers = response1.json()
    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": "-1", "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    assert response.status_code == 422


def date_time_convert(t: datetime.datetime) -> str:
    return f"{t.year:04}-{t.month:02}-{t.day:02}T{t.hour:02}:{t.minute:02}:{t.second:02}.{t.microsecond:03}Z"


async def test_get_messages_from_chat_ok(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася7"})
    chatusers = response1.json()

    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    mesg = response.json()

    response2 = await ac.post("/message_service/get_messages_from_chat", json={"user_id": chatusers['user_id'],"chat_id": chatusers['chat_id'], "count": 10, "offset_message_id": -1})

    assert response2.status_code == 200


async def test_get_messages_from_chat_count(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася6"})
    chatusers = response1.json()

    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    mesg = response.json()

    response2 = await ac.post("/message_service/get_messages_from_chat", json={"chat_id": chatusers['user_id'], "count": -1, "offset_message_id": -1})

    assert response2.status_code == 422


async def test_get_messages_from_chat_user(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася5"})
    chatusers = response1.json()

    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    mesg = response.json()

    response2 = await ac.post("/message_service/get_messages_from_chat", json={"user_id": -1,"chat_id": chatusers['chat_id'], "count": 10, "offset_message_id": -1})

    assert response2.status_code == 422


async def test_get_messages_from_wating_chat_ok(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася4"})
    chatusers = response1.json()

    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers["chat_id"], "sender_id": chatusers["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    mesg = response.json()

    response2 = await ac.post("/message_service/get_messages_from_wating_chat", json={"chat_id": chatusers['chat_id'], "count": 10, "offset_message_id": -1})
    print(response2.text)
    assert response2.status_code == 200


async def test_get_messages_from_wating_chat_not_wating_chat(ac: AsyncClient):
    response1 = await ac.post("/message_service/user_registration/bot", json={"platform_name": "telegram", "name": "Вася4"})
    chatusers1 = response1.json()

    response2 = await ac.post("/message_service/user_registration/web", json={"platform_name": "web", "name": "AAAaaaa4"})
    chatusers2 = response2.json()

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": chatusers2["user_id"], "chat_id": chatusers1["chat_id"]})
    
    response = await ac.post("/message_service/send_a_message_to_chat", json={"id": 0, "chat_id": chatusers1["chat_id"], "sender_id": chatusers1["user_id"], "sended_at": date_time_convert(datetime.datetime.now()), "text": "xafasdfas"})
    mesg = response.json()

    response3 = await ac.post("/message_service/get_messages_from_wating_chat", json={"chat_id": chatusers1['chat_id'], "count": 10, "offset_message_id": -1})

    print(response3.text)
    assert response3.status_code == 422