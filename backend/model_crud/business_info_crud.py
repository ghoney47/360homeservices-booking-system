from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import BusinessInfo
from schemas import BusinessInfoBase, BusinessInfoCreate, BusinessInfoUpdate
from logging import warning

#create or get
async def get_or_create_business_info(update: BusinessInfoUpdate, db: AsyncSession):
    stmt = select(BusinessInfo).where(BusinessInfo.id == 1)
    result = await db.execute(stmt)
    info = result.scalar_one_or_none()

    if not info:
        warning("Business Information has not been Initialized")
        stmt = insert(BusinessInfo).values(
            id=1,
            total_estimates=0,
            business_name=update.business_name 
        ).returning(BusinessInfo)

        result = await db.execute(stmt)
        info = result.scalar_one()
        await db.commit()
    else:
        for k, v in update.model_dump().items():
            if v is not None:
                setattr(info, k, v)

        await db.commit()
        await db.refresh(info)
    
    return info


#increment total estimates by one
async def increment_total_estimates(db: AsyncSession):
    stmt = select(BusinessInfo).where(BusinessInfo.id == 1)
    result = await db.execute(stmt)
    info = result.scalar_one_or_none()

    if not info:
        # Auto-initialize if the record hasn't been seeded yet
        stmt = insert(BusinessInfo).values(
            id=1, total_estimates=1, business_name="LandscapePro"
        ).returning(BusinessInfo)
        result = await db.execute(stmt)
        info = result.scalar_one()
        await db.commit()
        return info

    info.total_estimates += 1
    await db.commit()
    await db.refresh(info)
    return info


#decrement total estimates by one
async def decrement_total_estimates(db: AsyncSession):
    stmt = select(BusinessInfo).where(BusinessInfo.id == 1)
    result = await db.execute(stmt)
    info = result.scalar_one_or_none()

    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Business Information has not been initialized"
        )
    
    info.total_estimates -= 1
    await db.commit()
    await db.refresh(info)
    return info
        

#update name
async def update_name(update: BusinessInfoUpdate, db: AsyncSession):
    new_name = update.business_name
    stmt = select(BusinessInfo).where(BusinessInfo.id == 1)
    result = await db.execute(stmt)
    info = result.scalar_one_or_none()

    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Business Information has not been initialized"
        )       

    if update.business_name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="business_name is required"
        )
    
    info.business_name = update.business_name

    await db.commit()
    await db.refresh(info)
    return info
