from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from ..settings import settings
from typing import AsyncGenerator

engine = create_async_engine(
    url=settings.DATABASE_URL_ASINC,
    echo=settings.DB_ECHO,
    pool_size=5,
    max_overflow=10
)

session_factory = async_sessionmaker(autocommit=False, bind=engine)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session