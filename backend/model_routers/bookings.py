from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date, time, datetime
from database import get_db
from schemas import ConfirmedBookingCreate, ConfirmedBookingUpdate, ConfirmedBookingResponse
from model_crud import bookings_crud as bc
from services.availability_service import book_slot, get_openings

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/create", response_model=ConfirmedBookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(booking: ConfirmedBookingCreate, db: AsyncSession = Depends(get_db)):
    return await book_slot(booking, db)


@router.get("/openings", response_model=List[datetime])
async def get_openings_endpoint(
    duration: int,
    start_date: date,
    op_start: time,
    op_end: time,
    dead_start: time,
    dead_end: time,
    db: AsyncSession = Depends(get_db),
):
    return await get_openings(duration, start_date, op_start, op_end, dead_start, dead_end, db)


@router.get("/", response_model=List[ConfirmedBookingResponse])
async def get_all_bookings_endpoint(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await bc.get_all_bookings(db, skip, limit)


@router.get("/{booking_hash}", response_model=ConfirmedBookingResponse)
async def get_booking_endpoint(booking_hash: str, db: AsyncSession = Depends(get_db)):
    return await bc.get_booking(booking_hash, db)


@router.patch("/{booking_hash}", response_model=ConfirmedBookingResponse)
async def update_booking_endpoint(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession = Depends(get_db)):
    return await bc.update_booking(update, booking_hash, db)


@router.patch("/assignemployees/{booking_hash}", response_model=ConfirmedBookingResponse)
async def assign_employees_endpoint(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession = Depends(get_db)):
    if update.assigned_employees is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No employees were provided",
        )
    return await bc.assign_employees(update.assigned_employees, booking_hash, db)


@router.patch("/removeemployees/{booking_hash}", response_model=ConfirmedBookingResponse)
async def remove_employees_endpoint(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession = Depends(get_db)):
    if update.assigned_employees is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No employees were provided",
        )
    return await bc.remove_employees(update.assigned_employees, booking_hash, db)


@router.delete("/delete/{booking_hash}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking_endpoint(booking_hash: str, db: AsyncSession = Depends(get_db)):
    return await bc.delete_booking(booking_hash, db)
