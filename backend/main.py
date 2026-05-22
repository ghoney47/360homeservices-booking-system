import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # picks up backend/.env in development; no-op in production if not present

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from model_routers.model_api import api_router
from limiter import limiter
import logging

# ── Mode switch ────────────────────────────────────────────────────────────────
# DB_MODE=sheets   → Google Sheets is the data store (no database needed)
# DB_MODE=postgres → original Postgres/Alembic behaviour
DB_MODE = os.getenv("DB_MODE", "postgres")

# ── CORS ───────────────────────────────────────────────────────────────────────
# Set ALLOWED_ORIGINS in .env as a comma-separated list of allowed origins.
# Defaults to localhost:5173 for development.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]


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

app = FastAPI(lifespan=lifespan)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
