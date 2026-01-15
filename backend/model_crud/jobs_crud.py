from typing import List
from models import Job
from schemas import JobCreate, JobResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from fastapi import HTTPException, status

#create
async def create_job(job: JobCreate, db: AsyncSession):
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
async def get_all_jobs(db: AsyncSession, skip: int = 0, limit: int = 100):
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
async def get_job(job_id: int, db: AsyncSession):
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
async def update_job(job_id: int, job_update: JobCreate, db: AsyncSession):
    """
    Updates job object of specified id

    Args:
        job_id (int): job id to be updated
        job_update (JobCreate): Update schema
        db (AsyncSession): database connection

    Raises:
        HTTPException: If job id does not exist, raises exception

    Returns:
        Job: updated job
    """
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
        if v is not None:
            setattr(job, k, v)

    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

#delete
async def delete_job(job_id: int, db: AsyncSession):
    """
    Deletes job with specified job id

    Args:
        job_id (int): job id
        db (AsyncSession): database connection

    Raises:
        HTTPException: if job id inputted does not exist

    Returns:
        None
    """
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

#delete
