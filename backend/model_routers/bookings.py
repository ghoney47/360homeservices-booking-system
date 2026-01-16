from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import ConfirmedBooking
from schemas import ConfirmedBookingCreate, ConfirmedBookingUpdate, ConfirmedBookingResponse
from model_crud import bookings_crud as bc

router = APIRouter(prefix="/bookings", tags=["Bookings"])

#create
@router.post("/create", response_model=ConfirmedBookingResponse)
async def create_booking_endpoint(booking: ConfirmedBookingCreate, db: AsyncSession = Depends(get_db)):
    return await bc.create_booking(booking, db)

#get all
@router.get("/", response_model=ConfirmedBookingResponse)
async def get_all_bookings_endpoint(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    return await bc.get_all_bookings(db, skip, limit)


#get one
@router.get("/{booking_hash}", response_model=ConfirmedBookingResponse)
async def get_booking_endpoint(booking_hash: str, db: AsyncSession = Depends(get_db)):
    return await bc.get_booking(booking_hash, db)

#update
@router.patch("/{booking_hash}", response_model=ConfirmedBookingResponse)
async def update_booking_endpoint(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession = Depends(get_db)):
    return await bc.update_booking(update, booking_hash, db)


#assign employees
@router.patch("/assignemployees/{booking_hash}", response_model=ConfirmedBookingResponse)
async def assign_employees_endpoint(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession = Depends(get_db)):
    if update.assigned_employees is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No employees were inputted"
        )
    
    employee_list = update.assigned_employees

    return await bc.assign_employees(employee_list, booking_hash, db)

#remove employees
@router.patch("/removeemployees/{booking_hash}", response_model=ConfirmedBookingResponse)
async def remove_employees_endpoint(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession = Depends(get_db)):
    if update.assigned_employees is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No employees were inputted"
        )
    
    employee_list = update.assigned_employees
    
    return await bc.remove_employees(employee_list, booking_hash, db)


#delete
@router.delete("/delete/{booking_hash}")
async def delete_booking_endpoint(booking_hash: str, db: AsyncSession = Depends(get_db)):
    return await bc.delete_booking(booking_hash, db)