import asyncio
import logging
import os
from sqlalchemy import text
from backend.database import engine, Base

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

#AFTER WIPE RUN THIS IN DIRECTORY OF THE DATABASE after deleting all versions of alembic
"""
alembic revision --autogenerate -m "initial tables"

then 

alembic upgrade head
"""

# DEV ONLY — DO NOT USE IN PRODUCTION!!!!!
async def wipe_database():
    """
    Completely wipes the database schema and recreates it.
    Resets all sequences. DEV USE ONLY.
    """
    async with engine.begin() as conn:
        logging.warning("Dropping public schema (DEV ONLY)...")
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

        logging.warning("Recreating tables...")
        await conn.run_sync(Base.metadata.create_all)

        logging.warning("Database wipe complete (schema + sequences reset).")


# Main entry point
async def main():
    logging.warning("Starting DEV database wipe...")
    await wipe_database()
    logging.warning("DEV database wipe finished successfully.")


if __name__ == "__main__":
    asyncio.run(main())
