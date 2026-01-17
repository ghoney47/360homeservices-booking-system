import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator

DATABASE_URL = "postgresql+asyncpg://postgres:icEking08@localhost:5432/primary"

# declaring datebase connection and session
engine = create_async_engine(DATABASE_URL, echo=True)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
metadata = Base.metadata

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Docstring for get_db
    
    :return: database for use in routers
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with Session() as session:
        try:
            yield session
        finally:
            await session.close()
