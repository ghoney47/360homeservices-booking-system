from fastapi import APIRouter, Depends
from .employees import router as employees_router
from .jobs import router as jobs_router
from .clients import router as clients_router
from .addresses import router as addresses_router
from .bookings import router as bookings_router
from .business_info import router as business_info_router
from service_routers.services import router as services_router
from service_routers.booking_intake import router as intake_router
from auth import require_api_key

api_router = APIRouter(prefix="/api/v1")

# ── DB-backed admin routes — require API key (also 503 in Sheets mode) ─────────
_admin = {"dependencies": [Depends(require_api_key)]}
api_router.include_router(employees_router, **_admin)
api_router.include_router(jobs_router, **_admin)
api_router.include_router(clients_router, **_admin)
api_router.include_router(addresses_router, **_admin)
api_router.include_router(bookings_router, **_admin)
api_router.include_router(business_info_router, **_admin)

# ── Public service routes (no auth required) ──────────────────────────────────
api_router.include_router(services_router)

# ── Sheets-backed customer intake routes (public) ────────────────────────────
api_router.include_router(intake_router)
