from contextlib import asynccontextmanager
from database import engine, Base
import models
from fastapi import FastAPI
from model_routers.model_api import api_router
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.warning("App starting. Models Loaded:")
    logging.warning(list(Base.metadata.tables.keys()))

    # run DDL before app starts
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    #TODO: optional? shutdown logic here



app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
logging.warning('APP ROUTES:')
logging.warning(app.routes)




