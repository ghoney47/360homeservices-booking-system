from contextlib import asynccontextmanager
from database import engine, Base
import models
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):

    # run DDL before app starts
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    #TODO: optional? shutdown logic here


app = FastAPI(lifespan=lifespan)