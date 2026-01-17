import asyncio
from database import engine
from utils.db_utils import wipe_database

#for dev only

async def main():
    await wipe_database(engine)

if __name__ == "__main__":
    asyncio.run(main())
