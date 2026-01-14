from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from database import get_db
from typing import Optional, List
from models import Employee
from schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate

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
async def get_all_employees(db: AsyncSession, skip: int = 0, limit: int = 100):
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