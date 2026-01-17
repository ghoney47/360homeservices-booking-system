from sqlalchemy import text
from database import engine, Base
import asyncio
import logging

#only database usage

async def wipe_database():
    """
    Wipes all tables and resets sequences in the database.
    WARNING: This will DELETE ALL DATA.
    """
    async with engine.begin() as conn:
        # 1️⃣ Drop all tables
        logging.warning("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)

        # 2️⃣ Recreate all tables
        logging.warning("Recreating all tables...")
        await conn.run_sync(Base.metadata.create_all)

        # 3️⃣ Reset all sequences
        logging.warning("Resetting sequences...")
        # Find all sequence names automatically
        result = await conn.execute(
            text(
                """
                SELECT relname FROM pg_class
                WHERE relkind='S';  -- 'S' = sequence
                """
            )
        )
        sequences = [row[0] for row in result.all()]
        for seq in sequences:
            await conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))

        logging.warning("Database wiped and sequences reset successfully.")

