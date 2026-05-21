from fastapi import APIRouter
from .employees import router as employees_router
from .jobs import router as jobs_router
from .clients import router as clients_router
from .addresses import router as addresses_router
from .bookings import router as bookings_router
from .business_info import router as business_info_router
from service_routers.services import router as services_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(employees_router)
api_router.include_router(jobs_router)
api_router.include_router(clients_router)
api_router.include_router(addresses_router)
api_router.include_router(bookings_router)
api_router.include_router(business_info_router)
api_router.include_router(services_router)
