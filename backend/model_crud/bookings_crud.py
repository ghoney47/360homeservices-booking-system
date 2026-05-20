from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import ConfirmedBooking, Employee
from schemas import ConfirmedBookingCreate, ConfirmedBookingUpdate, ConfirmedBookingResponse
from utils.validators import client_exists, address_exists


#create
async def create_booking(booking: ConfirmedBookingCreate, db: AsyncSession):
    """creates ConfirmedBooking Object

    Args:
        booking (ConfirmedBookingCreate): create schema
        db (AsyncSession): database connection  

    Raises:
        HTTPException: raises 404 if client id is not found
        HTTPException: raises 404 if address id is not found

    Returns:
        ConfirmedBooking: new booking
    """
    #check address and client are valid
    if not await client_exists(booking.client_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {booking.client_id} does not exist"
        )

    if not await address_exists(booking.address_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address {booking.address_id} does not exist"
        )

    # assigned_employees is M2M — exclude from column insert
    import uuid
    row_data = booking.model_dump(exclude={"assigned_employees"})
    row_data["id_hash"] = str(uuid.uuid4())

    stmt = insert(ConfirmedBooking).values(**row_data).returning(ConfirmedBooking)
    result = await db.execute(stmt)

    await db.commit()

    new_booking = result.scalar_one_or_none()

    return new_booking


#get all 
async def get_all_bookings(db: AsyncSession, skip: int, limit: int):
    """gets all bookings in database

    Args:
        db (AsyncSession): database connection
        skip (int): rows skipped
        limit (int): rows shown

    Returns:
        list[ConfirmedBooking] : list of all bookings stored
    """

    stmt = select(ConfirmedBooking).offset(skip).limit(limit)
    result = await db.execute(stmt)
    bookings = result.scalars().all()

    return bookings

#get one
async def get_booking(booking_hash: str, db: AsyncSession):
    """Gets a booking based on its hash

    Args:
        booking_hash (str): hash of booking object
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if hash not found

    Returns:
        ConfirmedBooking: specified booking
    """
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
    """updates status or price of booking

    Args:
        update (ConfirmedBookingUpdate): update schema (employee list should be null)
        booking_hash (str): hash id of booking object
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if booking does not exist

    Returns:
        ConfirmedBooking: updated booking
    """
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
    
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking

#remove employees
async def remove_employees(employee_ids: list[int], booking_hash: str, db: AsyncSession):
    """removes employees from a booking

    Args:
        employee_ids (list[int]): employee ids to be removed
        booking_hash (str): booking hash id
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if the booking does not exist

    Returns:
        ConfirmedBooking: updated booking
    """
    booking = await db.get(ConfirmedBooking, booking_hash)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_hash} not found"
        )
    
    #gets all assigned employees
    employees = [await db.get(Employee, e_id) for e_id in employee_ids]

    #removes employees
    for e in employees:
        if e in booking.assigned_employees:
            booking.assigned_employees.remove(e)

    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


#assign employees
async def assign_employees(employee_ids: list[int], booking_hash: str, db: AsyncSession):
    """assigns employees to a booking

    Args:
        employee_ids (list[int]): employee ids
        booking_hash (str): booking hash id
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if the booking hash does not exist

    Returns:
        ConfirmedBooking: updated booking
    """
    
    booking = await db.get(ConfirmedBooking, booking_hash)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_hash} not found"
        )
    
    #gets all assigned employees
    employees = [await db.get(Employee, e_id) for e_id in employee_ids]

    #adds from booking
    for e in employees:
        if e not in booking.assigned_employees:
            booking.assigned_employees.append(e)

    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking

#delete
async def delete_booking(booking_hash: str, db: AsyncSession):
    """deletes booking

    Args:
        booking_hash (str): booking hash
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if the hash does not exist

    Returns:
        None
    """
    stmt = select(ConfirmedBooking).where(ConfirmedBooking.id_hash == booking_hash)
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_hash} not found"
        )

    await db.delete(booking)
    await db.commit()
    return None