from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from model_crud import jobs_crud as jc
from schemas import JobCreate, JobResponse
from typing import List

#Job router
router = APIRouter(prefix="/jobs", tags=["Jobs"]) 

#create
@router.post("/create", response_model=JobResponse, status_code= status.HTTP_201_CREATED)
async def create_job_endpoint(job: JobCreate, db: AsyncSession = Depends(get_db)):
    return await jc.create_job(job, db)
  

#get all
@router.get("/", response_model=List[JobResponse])
async def get_all_jobs_endpoint(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    return await jc.get_all_jobs(db, skip, limit)



#get one
@router.get("/{job_id}", response_model = JobResponse)
async def get_job_endpoint(job_id: int, db: AsyncSession = Depends(get_db)):
    return await jc.get_job(job_id, db)


#update
@router.patch("/update/{job_id}")
async def update_job_endpoint(job_id: int, job_update: JobCreate, db: AsyncSession = Depends(get_db)):
    return await jc.update_job(job_id, job_update, db)

#delete 
@router.delete("/delete/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_endpoint(job_id: int, db: AsyncSession = Depends(get_db)):
    return await jc.delete_job(job_id, db)



