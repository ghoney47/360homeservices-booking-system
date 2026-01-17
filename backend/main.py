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
    
    # Initialize business_info if needed
    async with engine.begin() as conn:
        def init_business_info(sync_conn):
            
            session = Session(bind=sync_conn)
            info = session.query(BusinessInfo).filter(BusinessInfo.id == 1).first()
            
            if not info:
                logging.warning("Creating initial business_info row")
                info = BusinessInfo(id=1, total_estimates=0, business_name="")
                session.add(info)
                session.commit()
        
        await conn.run_sync(init_business_info)
    
    yield
    # Shutdown logic here

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)