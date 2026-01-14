from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from database import get_db
from typing import Optional, List
from models import Employee
from schemas import EmployeeBase, EmployeeCreate, EmployeeResponse

#create router
router = APIRouter(prefix="/employees", tags=["Employees"])


#create
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, db: AsyncSession = Depends(get_db)):
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
@router.get("/", response_model=EmployeeResponse)
async def get_employees(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
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
@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
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
@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(employee: EmployeeCreate)

#add assigned booking(s)

#delete