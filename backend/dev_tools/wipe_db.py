import asyncio
from dev_tools.db_utils import wipe_database

#for dev only

async def main():
    await wipe_database()

if __name__ == "__main__":
    asyncio.run(main())
