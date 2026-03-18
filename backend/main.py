from contextlib import asynccontextmanager
from database import engine, Base
import models
from fastapi import FastAPI
from model_routers.model_api import api_router
import logging
import subprocess
from sqlalchemy.orm import Session
from models import BusinessInfo
from fastapi.middleware.cors import CORSMiddleware



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

# Vite port for frontend
origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
