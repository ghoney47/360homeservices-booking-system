from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import ConfirmedBooking
from schemas import ConfirmedBookingCreate, ConfirmedBookingUpdate, ConfirmedBookingResponse
from utils.validators import client_exists, address_exists

#create
async def create_booking(booking: ConfirmedBookingCreate, db: AsyncSession):
    #check address and client are valid
    if not client_exists(booking.client_id, db):
        raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Client {booking.client_id} does not exist"
        )
    
    if not address_exists(booking.address_id, db):
        raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Address {booking.address_id} does not exist"
        )

    stmt = insert(ConfirmedBooking).values(**booking.model_dump()).returning(ConfirmedBooking)
    result = await db.execute(stmt)

    await db.commit()

    new_booking = result.scalar_one_or_none()
    return new_booking


#get all 
async def get_all_bookings(db: AsyncSession, skip = 0, limit = 100):
    stmt = select(ConfirmedBooking).offset(skip).limit(limit)
    result = await db.execute(stmt)
    bookings = result.scalars().all()

    return bookings

#get one
async def get_booking(booking_hash: str, db: AsyncSession):
    stmt = select(ConfirmedBooking).where(ConfirmedBooking.id_hash == booking_hash)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_hash} not found"
        )

    return booking

#update
async def update_booking(update: ConfirmedBookingUpdate, booking_hash: str, db: AsyncSession):
    stmt = select(ConfirmedBooking).where(ConfirmedBooking.id_hash == booking_hash)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_hash} not found"
        )
    
    #updating values
    for k, v in update.model_dump().items():
        if v is not None:
            setattr(booking, k, v)
    
