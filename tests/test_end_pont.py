from httpx import AsyncClient
from conftest import async_session_maker
from src.database.database_requests import *

from tests.test_utility import comparison

import datetime

STR_31 = "1234567890123456789012345678901"
STR_256 = "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"

TELEGRAM_NAME = "Telegram"
TELEGRAM_URL = "http://localhost:8001"
WEB_NAME = "web"
WEB_URL = "http://localhost:8001"

TELEGRAM = PlatformDTO(id=-1, platform_type="bot",platform_name=TELEGRAM_NAME,url=TELEGRAM_URL)
WEB = PlatformDTO(id=-1, platform_type="web",platform_name=WEB_NAME,url=WEB_URL)

BOT1_USER = UserDTO(id=-1, platform_id=-1, name="Вова")
BOT1_CHAT = ChatDTO(id=-1, name="Вова")

BOT2_USER = UserDTO(id=-1, platform_id=-1, name="AAA")
BOT2_CHAT = ChatDTO(id=-1, name="AAA")

BOT3_USER = UserDTO(id=-1, platform_id=-1, name="BBB")
BOT3_CHAT = ChatDTO(id=-1, name="BBB")

WEB1_USER = UserDTO(id=-1, platform_id=-1, name="Ваня")

WEB2_USER = UserDTO(id=-1, platform_id=-1, name="Вася")

MESSAGE1 = MessageDTO(id=-1, chat_id=-1,sender_id=-1,sended_at= datetime.datetime.now(), text="asdas")

MESSAGE2 = MessageDTO(id=-1, chat_id=-1,sender_id=-1,sended_at=datetime.datetime.now(), text="asdas1")

MESSAGE3 = MessageDTO(id=-1, chat_id=-1,sender_id=-1,sended_at=datetime.datetime.now(), text="asdas2")

async def test_prep():
    async with async_session_maker() as session:
        await session.execute(delete(MessageORM))
        await session.execute(delete(ChatUsersORM))
        await session.execute(delete(ChatORM))
        await session.execute(delete(WaitingСhatORM))
        await session.execute(delete(UserORM))
        await session.execute(delete(PlatformORM))
        await session.commit()
    assert 1 == 1


async def test_platform_registration_ok(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bot", json=TELEGRAM.model_dump())
    assert response.json() == {"status": "ok"}


async def test_platform_registration_type(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/bots", json=TELEGRAM.model_dump())
    assert response.status_code == 422


async def test_platform_registration_name_30(ac: AsyncClient):
    dict_platform = TELEGRAM.model_dump()
    dict_platform["platform_name"] = STR_31
    response = await ac.post("/message_service/platform_registration/bot", json=dict_platform)
    assert response.status_code == 422


async def test_platform_registration_url_256(ac: AsyncClient):
    dict_platform = TELEGRAM.model_dump()
    dict_platform["url"] = STR_256
    response = await ac.post("/message_service/platform_registration/bot", json=dict_platform)
    assert response.status_code == 422


async def test_user_registration_bot_ok(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": TELEGRAM_NAME, "name": BOT1_USER.model_dump()["name"]})
    js = response.json()
    BOT1_USER.id = int(js["user_id"])
    BOT1_CHAT.id = int(js["chat_id"])
    assert response.status_code == 200


async def test_user_registration_bot_platform_name_30(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": STR_31, "name": BOT1_USER.model_dump()["name"]})
    assert response.status_code == 422


async def test_user_registration_bot_name_256(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": TELEGRAM_NAME, "name": STR_256})
    assert response.status_code == 422


async def test_user_registration_bot_platform_not_found(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": "not_fund", "name": BOT1_USER.model_dump()["name"]})
    assert response.status_code == 422


async def test_platform_registration_web_ok(ac: AsyncClient):
    response = await ac.post("/message_service/platform_registration/web", json=WEB.model_dump())
    assert response.status_code == 200


async def test_user_registration_web_ok(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": WEB_NAME, "name": WEB1_USER.model_dump()["name"]})
    js = response.json()
    WEB1_USER.id = int(js["user_id"])
    assert response.status_code == 200


async def test_user_registration_web_platform_name_30(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": STR_31, "name": WEB1_USER.model_dump()["name"]})
    assert response.status_code == 422


async def test_user_registration_web_name_256(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": WEB_NAME, "name": STR_256})
    assert response.status_code == 422


async def test_user_registration_web_platform_not_fund(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": "web1", "name": WEB1_USER.model_dump()["name"]})
    assert response.status_code == 422


async def test_get_list_of_waiting_chats_ok(ac: AsyncClient):
    response = await ac.post("/message_service/get_list_of_waiting_chats", json='10')
    js = response.json()
    assert js == [BOT1_CHAT.model_dump()]


async def test_get_list_of_waiting_chats_count(ac: AsyncClient):
    response = await ac.post("/message_service/get_list_of_waiting_chats", json='-1')
    assert response.status_code == 422


async def test_get_chats_by_user_ok(ac: AsyncClient):
    response = await ac.post("/message_service/get_chats_by_user", json=BOT1_USER.id)
    js = response.json()
    assert js == [BOT1_CHAT.model_dump()]


async def test_get_chats_by_user_user_not_found(ac: AsyncClient):
    response = await ac.post("/message_service/get_chats_by_user", json="-1")
    js = response.json()
    assert js == []


async def test_get_users_by_chat_id_ok1(ac: AsyncClient):
    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": WEB1_USER.id, "chat_id": BOT1_CHAT.id})

    users = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": WEB1_USER.id, "chat_id": BOT1_CHAT.id})

    js = users.json()

    assert comparison(UserDTO.model_validate(js[0],from_attributes=True), BOT1_USER, ["platform_id"]) and comparison(UserDTO.model_validate(js[1],from_attributes=True),WEB1_USER, ["platform_id"]) == True


async def test_get_users_by_chat_id_ok2(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": TELEGRAM_NAME, "name": BOT2_USER.model_dump()["name"]})
    js = response.json()
    BOT2_USER.id = int(js["user_id"])
    BOT2_CHAT.id = int(js["chat_id"])

    users = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": "-1", "chat_id": BOT2_CHAT.id})
    assert users.status_code == 200


async def test_get_users_by_chat_id_chat_not_found(ac: AsyncClient):
    response = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": BOT2_USER.id, "chat_id": "-1"})
    assert response.status_code == 422


async def test_get_users_by_chat_id_user_not_found(ac: AsyncClient):
    users = await ac.post("/message_service/get_users_by_chat_id", json={"user_id": BOT2_USER.id, "chat_id":BOT1_CHAT.id})
    assert users.status_code == 422


async def test_connect_to_a_waiting_chat_ok(ac: AsyncClient):
    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": WEB1_USER.id, "chat_id": BOT2_CHAT.id})
    js = response.json()
    assert js == BOT2_CHAT.model_dump()


async def test_connect_to_a_waiting_chat_already_in_chat(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/bot", json={"platform_name": TELEGRAM_NAME, "name": BOT3_USER.model_dump()["name"]})
    js = response.json()
    BOT3_USER.id = int(js["user_id"])
    BOT3_CHAT.id = int(js["chat_id"])

    response = await ac.post("/message_service/connect_to_a_waiting_chat", json={"user_id": BOT3_USER.id, "chat_id": BOT3_CHAT.id})
    assert response.status_code == 422


async def test_connect_user_to_chat_ok(ac: AsyncClient):
    response = await ac.post("/message_service/user_registration/web", json={"platform_name": WEB_NAME, "name": WEB2_USER.model_dump()["name"]})
    js = response.json()
    WEB2_USER.id = int(js["user_id"])

    response = await ac.post("/message_service/connect_user_to_chat", json={"user_id": WEB2_USER.id, "chat_id": BOT1_CHAT.id})
    assert response.json() == {"user_id": WEB2_USER.id, "chat_id": BOT1_CHAT.id}


async def test_connect_user_to_chat_already_in_chat(ac: AsyncClient):
    response = await ac.post("/message_service/connect_user_to_chat", json={"user_id": WEB2_USER.id, "chat_id": BOT1_CHAT.id})
    assert response.status_code == 422


async def test_send_a_message_to_chat_ok(ac: AsyncClient):
    MESSAGE1.chat_id = BOT1_USER.id
    MESSAGE1.sender_id = BOT1_USER.id

    dict_msg = MESSAGE1.model_dump()
    dict_msg["sended_at"] = MESSAGE1.sended_at.isoformat()

    response = await ac.post("/message_service/send_a_message_to_chat", json=dict_msg)
    assert response.json() == {"status": "ok"}


async def test_send_a_message_to_chat_not_fund_user_in_chat(ac: AsyncClient):
    MESSAGE2.sender_id=BOT1_USER.id
    MESSAGE2.chat_id=BOT2_CHAT.id

    dict_msg = MESSAGE2.model_dump()
    dict_msg["sended_at"] = MESSAGE2.sended_at.isoformat()

    response = await ac.post("/message_service/send_a_message_to_chat", json=dict_msg)
    assert response.status_code == 422


async def test_get_messages_from_chat_ok(ac: AsyncClient):
    response2 = await ac.post("/message_service/get_messages_from_chat", json={"user_id": MESSAGE1.sender_id, "chat_id": MESSAGE1.chat_id, "count": 10, "offset_message_id": -1})
    js = response2.json()
    js[0]["sended_at"] = MESSAGE1.sended_at

    assert comparison(MessageDTO.model_validate(js[0],from_attributes=True),MESSAGE1, ["id"]) == True


async def test_get_messages_from_chat_count(ac: AsyncClient):
    response2 = await ac.post("/message_service/get_messages_from_chat", json={"user_id": MESSAGE1.sender_id, "chat_id": MESSAGE1.chat_id, "count": -1, "offset_message_id": -1})

    assert response2.status_code == 422


async def test_get_messages_from_chat_user(ac: AsyncClient):
    response2 = await ac.post("/message_service/get_messages_from_chat", json={"user_id": BOT2_USER.id, "chat_id": MESSAGE1.chat_id, "count": 10, "offset_message_id": -1})
    
    assert response2.status_code == 422


async def test_get_messages_from_wating_chat_ok(ac: AsyncClient):
    MESSAGE3.sender_id=BOT3_USER.id
    MESSAGE3.chat_id=BOT3_CHAT.id

    dict_msg = MESSAGE3.model_dump()
    dict_msg["sended_at"] = MESSAGE3.sended_at.isoformat()

    response = await ac.post("/message_service/send_a_message_to_chat", json=dict_msg)
    mesg = response.json()

    response2 = await ac.post("/message_service/get_messages_from_wating_chat", json={"chat_id": BOT3_CHAT.id, "count": 10, "offset_message_id": -1})
    js = response2.json()
    js[0]["sended_at"] = MESSAGE3.sended_at

    assert comparison(MessageDTO.model_validate(js[0],from_attributes=True),MESSAGE3, ["id"]) == True


async def test_get_messages_from_wating_chat_not_wating_chat(ac: AsyncClient):
    response3 = await ac.post("/message_service/get_messages_from_wating_chat", json={"chat_id": BOT1_CHAT.id, "count": 10, "offset_message_id": -1})

    assert response3.status_code == 422
