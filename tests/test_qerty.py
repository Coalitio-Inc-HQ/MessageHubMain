from conftest import async_session_maker
from src.database.database_requests import *
import datetime


def test_true():
    assert 1 == 1


async def test_platform_registration():
    async with async_session_maker() as session:
        res = await platform_registration(session=session, platform_type="bot", platform_name="telga", url="asdasd")
        assert res == PlatformDTO(
            id=res.id, platform_type="bot", platform_name="telga", url="asdasd")


async def test_bot_user_registration():
    async with async_session_maker() as session:
        res = await bot_user_registration(session=session, platform_name="telga", name="zxc")
        assert res == res


async def test_save_messege():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="zxcv")
        res = await save_messege(session=session, message=MessageDTO(id=None, chat_id=bot.chat_id, sender_id=bot.user_id, sended_at=datetime.datetime.now(), text="Hello world!"))
        assert res == res


async def test_get_users_by_chat_id():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="zxcv")
        user = (await session.execute(select(UserORM).where(UserORM.id == bot.user_id))).scalar()
        res = await get_users_by_chat_id(session=session, chat_id=bot.chat_id)
        assert res == [
            UserDTO(id=user.id, platform_id=user.platform_id, name=user.name)]


async def test_get_all_platform():
    async with async_session_maker() as session:
        res = await get_all_platform(session=session)
        assert res == res


async def test_get_platforms_by_chat_id():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_type="bot", platform_name="tst", url="asdasd")
        bot = await bot_user_registration(session=session, platform_name="tst", name="sad")
        res = await get_platforms_by_chat_id(session=session, chat_id=bot.chat_id)
        assert res == [plat]


async def test_get_platforms_by_name():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_type="bot", platform_name="tst1", url="asdasd")
        res = await get_platforms_by_name(session=session, platform_name="tst1")
        assert res == [plat]


async def test_update_platforms_by_name():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_type="bot", platform_name="tst2", url="asdasd")
        res = await update_platforms_by_name(session=session, platform_name="tst2", url="qwe")
        assert res == [PlatformDTO(
            id=plat.id, platform_name=plat.platform_name, platform_type=plat.platform_type, url="qwe")]


async def test_user_registration():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_type="bot", platform_name="3", url="asdasd")
        user = await user_registration(session=session, platform_name=plat.platform_name, name="asd")
        assert user == UserDTO(id=user.id, platform_id=plat.id, name="asd")


async def test_get_list_of_waiting_chats():
    async with async_session_maker() as session:
        user = await bot_user_registration(session=session, platform_name="telga", name="asxd")
        res = await get_list_of_waiting_chats(session=session, count=-1)
        funduser = None
        for row in res:
            if row.id == user.chat_id:
                funduser = row.id
        assert user.chat_id == funduser


async def test_connect_to_a_waiting_chat():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="asxd")
        user = await user_registration(session=session, platform_name="telga", name="zxc")

        res = await connect_to_a_waiting_chat(session=session, user_id=user.id, chat_id=bot.chat_id)

        assert bot.chat_id == res.id


async def test_connect_user_to_chat():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="asxd")
        user = await user_registration(session=session, platform_name="telga", name="zxc")

        res = await connect_user_to_chat(session=session, user_id=user.id, chat_id=bot.chat_id)

        assert bot.chat_id == res.chat_id


async def test_get_chats_by_user_id():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="asxdsad")

        res = await get_chats_by_user_id(session=session, user_id=bot.user_id)

        assert bot.chat_id == res[0].id


async def test_get_messges_from_chat():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="asxdsad")

        res = await get_messges_from_chat(session=session, chat_id=bot.chat_id, count=10, offset_message_id=-1)

        assert res == res


async def test_get_chat_by_id():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="asxфывdsad")

        res = await get_chat_by_id(session=session, chat_id=bot.chat_id)

        assert res.id == bot.chat_id


async def test_get_platform_by_user_id():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_name="sadsad", platform_type="web", url="asdasdasd")
        bot = await bot_user_registration(session=session, platform_name="sadsad", name="asxфывdsad")

        res = await get_platform_by_user_id(session=session, user_id=bot.user_id)

        assert res == plat


async def test_get_users_by_chat_id():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_name="sadsadasdasd", platform_type="web", url="asdasdasd")
        bot = await bot_user_registration(session=session, platform_name="sadsadasdasd", name="asxфывdxzcsad")
        user = await user_registration(session=session, platform_name="sadsadasdasd", name="xzcz")

        await connect_user_to_chat(session=session, user_id=user.id, chat_id=bot.chat_id)

        res = await get_users_by_chat_id(session=session,chat_id=bot.chat_id)

        s = UserDTO.model_validate((await session.execute(select(UserORM).where(UserORM.id==bot.user_id))).scalar(),from_attributes=True)

        assert res == [s,user]


async def test_whether_the_user_is_in_the_chat():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_name="ASD", platform_type="web", url="asdasdasd")
        bot = await bot_user_registration(session=session, platform_name="ASD", name="asxфывdxzcsad")
        res = await whether_the_user_is_in_the_chat(session=session,chat_id=bot.chat_id,user_id=bot.user_id)

        assert res == True

async def test_is_waiting_chat_1():
    async with async_session_maker() as session:
        plat = await platform_registration(session=session, platform_name="ASD", platform_type="web", url="asdasdasd")
        bot = await bot_user_registration(session=session, platform_name="ASD", name="asxфывdxzcsad")
        res = await is_waiting_chat(session=session,chat_id=bot.chat_id)

        assert res == True

async def test_is_waiting_chat_2():
    async with async_session_maker() as session:
        bot = await bot_user_registration(session=session, platform_name="telga", name="asxd")
        user = await user_registration(session=session, platform_name="telga", name="zxc")

        res = await connect_to_a_waiting_chat(session=session, user_id=user.id, chat_id=bot.chat_id)

        res = await is_waiting_chat(session=session,chat_id=bot.chat_id)

        assert res == False
