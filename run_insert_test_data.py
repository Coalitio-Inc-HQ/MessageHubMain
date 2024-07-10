import asyncio
from src.database.session_database import session_factory
from tests.insert_test_data import ins

async def insert_data():
    async with session_factory() as session:
        await ins(session=session)

asyncio.run(insert_data())
