from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
import asyncio

#use only in development
async def wipe_database(engine: AsyncEngine):
    """
    Wipes all tables in the 'public' schema of a PostgreSQL database.
    Resets all auto-increment IDs and handles foreign keys.
    """
    async with engine.begin() as conn:
        # fetch all table names dynamically
        result = await conn.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        if not tables:
            print("No tables found.")
            return

        # truncate all tables with restart identity and cascade
        truncate_sql = ";\n".join(
            f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE' for table in tables
        )
        await conn.execute(text(truncate_sql))
        print(f"Wiped tables: {tables}")


# Example usage with your async engine
if __name__ == "__main__":
    import database  # your module where engine is defined
    asyncio.run(wipe_database(database.engine))
