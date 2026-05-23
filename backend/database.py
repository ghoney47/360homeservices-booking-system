# Database is not used in production — app writes to Google Sheets via sheets_service.py.
# Base is kept so models.py can be imported without error; get_db is a 503 stub so
# DB-backed routers can be registered without crashing. Those routes will 503 if called.

from sqlalchemy.orm import declarative_base
from fastapi import HTTPException, status

Base = declarative_base()

# Engine / session commented out — Sheets deployment (DB_MODE=sheets).
# import os
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from typing import AsyncGenerator
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:<PASSWORD>@localhost:5432/primary")
# engine = create_async_engine(DATABASE_URL, echo=True)
# Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with Session() as session:
#         try:
#             yield session
#         finally:
#             await session.close()

async def get_db():
    # Sheets deployment — no database configured.
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Database not available in Sheets mode (DB_MODE=sheets)",
    )
