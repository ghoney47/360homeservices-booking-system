import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # picks up backend/.env in development; no-op in production if not present

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model_routers.model_api import api_router
import logging

# ── Mode switch ────────────────────────────────────────────────────────────────
# DB_MODE=sheets  → skip Postgres/Alembic startup (Google Sheets is the store)
# DB_MODE=postgres (default) → original behaviour
DB_MODE = os.getenv("DB_MODE", "postgres")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if DB_MODE == "postgres":
        import subprocess
        from database import Base
        import models  # noqa: F401 — registers ORM models with Base.metadata

        logging.warning("App starting. Models Loaded:")
        logging.warning(list(Base.metadata.tables.keys()))

        try:
            logging.warning("Running database migrations...")
            subprocess.run(["alembic", "upgrade", "head"], check=True)
            logging.warning("Migrations completed successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Migration failed: {e}")
            raise
    else:
        logging.warning(f"App starting in DB_MODE={DB_MODE!r} — skipping database init.")

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
