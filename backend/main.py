from contextlib import asynccontextmanager
from database import engine, Base
import models
from fastapi import FastAPI
from model_routers.model_api import api_router
import logging
import subprocess
from sqlalchemy.orm import Session
from models import BusinessInfo



@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.warning("App starting. Models Loaded:")
    logging.warning(list(Base.metadata.tables.keys()))
    
    # Run Alembic migrations on startup
    try:
        logging.warning("Running database migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logging.warning("Migrations completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Migration failed: {e}")
        raise
    
    yield
    # Shutdown logic here

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)