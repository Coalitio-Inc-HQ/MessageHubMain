from src.database.database_requests import *
from src.database.session_database import session_factory
import datetime


async def ins():
    async with session_factory() as session:
        telegram = await platform_registration(session=session, platform_type="bot", platform_name="Telegram", url="http://localhost:8002")
        web = await platform_registration(session=session, platform_type="web", platform_name="Web", url="http://localhost:8003")

        bot1 = await bot_user_registration(session=session, platform_name="Telegram", name="Володя")
        bot2 = await bot_user_registration(session=session, platform_name="Telegram", name="Игорь")
        bot3 = await bot_user_registration(session=session, platform_name="Telegram", name="Саша")

        user1 = await user_registration(session=session, platform_name="Web", name="Руслан")
        user2 = await user_registration(session=session, platform_name="Web", name="Борис")
        user3 = await user_registration(session=session, platform_name="Web", name="Паша")
        user4 = await user_registration(session=session, platform_name="Web", name="Коля")

        await connect_to_a_waiting_chat(session=session, user_id=user1.id, chat_id=bot1.chat_id)

        await connect_to_a_waiting_chat(session=session, user_id=user2.id, chat_id=bot2.chat_id)
        await connect_user_to_chat(session=session, user_id=user3.id, chat_id=bot2.chat_id)

        msg1 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot1.chat_id, sender_id=bot1.user_id, sended_at=datetime.datetime.now(), text="Hello!"))
        msg2 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot1.chat_id, sender_id=bot1.user_id, sended_at=datetime.datetime.now()+datetime.timedelta(0,3), text="How to pass the internship?"))
        msg3 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot1.chat_id, sender_id=user1.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,5), text="No comments."))
        msg4 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot1.chat_id, sender_id=bot1.user_id, sended_at=datetime.datetime.now()+datetime.timedelta(0,5), text=":("))

        msg5 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=bot2.user_id, sended_at=datetime.datetime.now(), text="Как дела?"))
        msg6 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=user1.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,3), text="Привет, спасибо. А у тебя?"))
        msg7 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=bot2.user_id, sended_at=datetime.datetime.now()+datetime.timedelta(0,5), text="Отлично, спасибо. С тобой случайно не встречался последнее время?"))
        msg8 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=user1.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,6), text=" Да, был занят работой. Новый проект идёт полным ходом."))
        msg9 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=bot2.user_id, sended_at=datetime.datetime.now()+datetime.timedelta(0,7), text="Звучит интересно. Расскажи, о чём он?"))
        msg10 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=user1.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,8), text=" Это разработка нового приложения для агрегации чатов."))
        msg11 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=user2.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,9), text="Интересная идея."))
        msg12 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=bot1.user_id, sended_at=datetime.datetime.now()+datetime.timedelta(0,10), text="Может быть."))
        msg13 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=user1.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,11), text="Да, точно. Именно поэтому я стараюсь делать этот проект максимально удобным и интуитивно понятным."))
        msg14 = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot2.chat_id, sender_id=user2.id, sended_at=datetime.datetime.now()+datetime.timedelta(0,12), text="Замечательно. Надеюсь, удастся."))



