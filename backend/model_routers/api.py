from fastapi import APIRouter
from .employees import router as employees_router
from .jobs import router as jobs_router
from .clients import router as clients_router
#TODO: add more routers here 

api_router = APIRouter(prefix="/api/v1")

__all__ = [
    "employees_router",
    "jobs_router",
    "clients_router"
]

api_router.include_router(employees_router)
api_router.include_router(jobs_router)
api_router.include_router(clients_router)