from src.database.database_requests import *
from sqlalchemy.ext.asyncio import AsyncSession
import datetime
import random

TELEGRAM_NAME = "Telegram"
WEB_NAME = "web"

COUNT_BOT_USERS = 10
COUNT_WEB_USERS = 0

CONUT_CONNECTED_BOT_USERS = 0
MAX_COUNT_CONNECTRD_WEB_USERS = 0

MAX_MESSAGES = 50

async def ins(session: AsyncSession):
    telegram = await platform_registration(session=session, platform_type="bot", platform_name=TELEGRAM_NAME, url="http://localhost:8002")
    web = await platform_registration(session=session, platform_type="web", platform_name=WEB_NAME, url="http://localhost:8000")

    for i in range(COUNT_BOT_USERS):
        await bot_user_registration(session=session, platform_name=TELEGRAM_NAME, name=f"Bot user {i}")

    for i in range(COUNT_WEB_USERS):
        await user_registration(session=session, platform_name=WEB_NAME, name=f"Web user {i}")

    for i in range (CONUT_CONNECTED_BOT_USERS):
        arr = []
        for j in range(MAX_COUNT_CONNECTRD_WEB_USERS):
            id = random.randint(COUNT_BOT_USERS,COUNT_BOT_USERS+COUNT_WEB_USERS)
            while (id in arr):
                id = random.randint(COUNT_BOT_USERS,COUNT_BOT_USERS+COUNT_WEB_USERS)
            arr.append(id)

            await connect_user_to_chat(session=session, user_id=id, chat_id=i+1)

    for i in range (CONUT_CONNECTED_BOT_USERS):
        for j in range(MAX_MESSAGES):
            await save_messege(session=session, message=MessageDTO(id=None, chat_id=i+1, sender_id=i+1, sended_at=datetime.datetime.now(), text=f"{j}: Hello!", attachments={}))