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
        assert res == [PlatformDTO(id=plat.id,platform_name=plat.platform_name,platform_type=plat.platform_type,url="qwe")]
