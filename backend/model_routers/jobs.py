from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from database import get_db
from typing import Optional, List
from models import Job
from schemas import JobBase, JobCreate, JobResponse

#Job router
router = APIRouter(prefix="/jobs", tags=["Jobs"]) 

#create
@router.post("/", response_model=JobResponse, status_code= status.HTTP_201_CREATED)
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    """
    Docstring for create_job
    
    :param job: job object parameters
    :type job: JobCreate
    :param db: database connection
    :type db: AsyncSession
    """

    stmt = insert(Job).values(**job.model_dump()).returning(Job)
    result = await db.execute(stmt)
    await db.commit()

    new_job = result.scalar_one()
    return new_job
  

#get all
@router.get("/", response_model=List[JobResponse])
async def get_jobs (skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Docstring for get_jobs
    
    :param skip: Rows to skip
    :type skip: int
    :param limit: Rows to show
    :type limit: int
    :param db: Database connection
    :type db: AsyncSession

    returns all stored jobs
    """
    stmt = select(Job).offset(skip).limit(limit)
    result = await db.execute(stmt)

    jobs = result.scalars().all()
    return jobs



#get one
@router.get("/{job_id}", response_model = JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """
    Docstring for get_job
    
    :param job_id: job id
    :type job_id: int
    :param db: database connection
    :type db: AsyncSession

    returns job associated with the inputted id
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()


    if not job:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    return job

#update
@router.patch("/{job_id}")
async def update_job(job_id: int, job_update: JobCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )

    #updating job
    for k, v in job_update.model_dump().items():
        setattr(job, k, v)

    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

#delete 
@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    await db.delete(job)
    await db.commit()
    return None



