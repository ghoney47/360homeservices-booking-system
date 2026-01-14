from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from database import get_db
from typing import Optional, List
from models import Employee
from schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from model_crud import employees_crud as ec

#create router
router = APIRouter(prefix="/employees", tags=["Employees"])


#create
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EmployeeResponse)
async def create_employee_endpoint(employee: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    return await ec.create_employee(employee, db)



#get all
@router.get("/", response_model=EmployeeResponse)
async def get_all_employees_endpoint(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await ec.get_all_employees(db, skip, limit)


#get one
@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee_endpoint(employee_id: int, db: AsyncSession = Depends(get_db)):
    return await ec.get_employee(employee_id, db)


#update
@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee_endpoint(employee_update: EmployeeUpdate, employee_id: int, db: AsyncSession = Depends(get_db)):
    return await ec.update_employee(employee_update, employee_id, db)


#assign booking(s)
@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def assign_bookings_endpoint(employee_id: int, booking_ids: list[int], db: AsyncSession = Depends(get_db)):
    return await ec.assign_bookings(employee_id, booking_ids, db)


#delete booking(s)
@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def remove_bookings_endpoint(employee_id: int, booking_ids: list[int], db: AsyncSession = Depends(get_db)):
    return await ec.remove_bookings(employee_id, booking_ids, db)


#delete
@router.delete("/{employee_id}", response_model=EmployeeResponse)
async def delete_employee_endpoint(employee_id: int, db: AsyncSession = Depends(get_db)):
    return await ec.delete_employee(employee_id, db)