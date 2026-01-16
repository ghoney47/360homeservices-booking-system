from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import BusinessInfo
from schemas import BusinessInfoResponse, BusinessInfoDetailedResponse, BusinessInfoUpdate, BusinessInfoEstimateResponse
from model_crud import business_info_crud as bc




router = APIRouter(
    prefix="/businessinfo",
    tags = ["Business Information"]
)


#create or get
@router.put("/", response_model=BusinessInfoResponse)
async def get_or_create_business_info_endpoint(update: BusinessInfoUpdate, db: AsyncSession = Depends(get_db))
    return await bc.get_or_create_business_info(update, db)

#get detailed informtion 
@router.put("/detailed", response_model=BusinessInfoDetailedResponse)
async def get_detailed_info_endpoint(update: BusinessInfoUpdate, db: AsyncSession = Depends(get_db)):
    return await bc.get_or_create_business_info(update, db)

#increment estimates
@router.patch("/incrementestimate", response_model=BusinessInfoEstimateResponse)
async def increment_total_estimates_endpoint(db: AsyncSession = Depends(get_db)):
    return await bc.increment_total_estimates(db)

#decrement estimates
@router.patch("/decrementestimate", response_model=BusinessInfoEstimateResponse)
async def decrement_total_estimates_endpoint(db: AsyncSession = Depends(get_db)):
    return await bc.decrement_total_estimates(db)


@router.patch("/updatename", response_model=BusinessInfoResponse)
async def update_name_endpoint(update: BusinessInfoUpdate, db: AsyncSession = Depends(get_db)):
    return await bc.update_name(update, db)