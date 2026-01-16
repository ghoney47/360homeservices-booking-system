from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from database import get_db
from typing import Optional, List
from models import Employee, ConfirmedBooking
from schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate, ConfirmedBookingUpdate

#create
async def create_employee(employee: EmployeeCreate, db: AsyncSession):
    """
    Docstring for create_employee
    
    :param employee: Employee object parameters
    :type employee: EmployeeCreate
    :param db: Database connection
    :type db: AsyncSession
    
    returns created employee
    """

    stmt = insert(Employee).values(**employee.model_dump()).returning(Employee)
    result = await db.execute(stmt)
    await db.commit()

    new_employee = result.scalar_one()
    return new_employee

#get all
async def get_all_employees(skip: int, limit: int, db: AsyncSession):
    """
    Docstring for get_employees
    
    :param skip: Offset amount (rows skipped)
    :type skip: int
    :param limit: Rows to be shown
    :type limit: int
    :param db: Database connection
    :type db: AsyncSession

    returns all employees
    """
    stmt = select(Employee).offset(skip).limit(limit)
    result = await db.execute(stmt)

    employees = result.scalars().all()
    return employees

#get one
async def get_employee(employee_id: int, db: AsyncSession):
    """
    Docstring for get_employee

    employee_id: integer employee id
    db: Database Connection
    """
    stmt = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")
    
    return employee

#update
async def update_employee(employee_update: EmployeeUpdate, employee_id: int, db: AsyncSession):
    """Updates employee phone number and/or email

    Args:
        employee_update (EmployeeUpdate): Update schema
        employee_id (int): employee id
        db (AsyncSession): database connection

    Raises:
        HTTPException: employee id not found, raises 404 exception
    Returns:
        Employee: updated employee
    """
    stmt = select(Employee).where(Employee.id == employee_id)
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} does not exist"
        )

    #updating employee
    for k, v in employee_update.model_dump().items():
        if v is not None:
            setattr(employee, k, v)

    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee

#add assigned booking
async def assign_bookings(employee_id: int, booking_ids: list[int], db: AsyncSession):
    """
    assigns bookings to an employee

    Args:
        employee_id (int): employee to modify
        booking_ids (list[int]): list of booking ids
        db (AsyncSession): database connection

    Raises:
        HTTPException: if employee id does not exist, raises 404 exception

    Returns:
        Employee: updated employee
    """
    employee = await db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} does not exist"
        )
    
    #grabs all ConfirmedBooking objects 
    bookings = [await db.get(ConfirmedBooking, b_id) for b_id in booking_ids]

    #assigns employee all bookings specified (no duplicates)
    for b in bookings:
        if b not in employee.assignd_jobs:
            employee.assigned_jobs.append(b)
    
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee

#remove assigned booking
async def remove_bookings(employee_id: int, booking_ids: list[int], db: AsyncSession):
    """
    removes assigned bookings from an employee

    Args:
        employee_id (int): employee to be modified
        booking_ids (list[int]): list of bookings to be removed
        db (AsyncSession): database connection

    Raises:
        HTTPException: if employee does not exist, raises 404 exception

    Returns:
        Employee: updated employee
    """
    employee = await db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} does not exist"
        )
    
    #grabs all ConfirmedBooking objects 
    bookings = [await db.get(ConfirmedBooking, b_id) for b_id in booking_ids]

    #removes bookings specified that were previously assigned
    for b in bookings:
        if b in employee.assignd_jobs:
            employee.assigned_jobs.remove(b)
    
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee

async def delete_employee(employee_id: int, db: AsyncSession):
    """deletes employee from the database

    Args:
        employee_id (int): employee to be deleted              
        db (AsyncSession): database connection

    Raises:
        HTTPException: if employee not found raises 404 exception

    Returns:
        None
    """
    employee = await db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} does not exist"
        )


    await db.delete(employee)
    await db.commit()
    return None



