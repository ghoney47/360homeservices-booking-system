from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import Address
from schemas import AddressCreate, AddressResponse, AddressUpdate

#create
async def create_address(address: AddressCreate, db: AsyncSession):
    stmt = insert(Address).values(**address.model_dump()).returning(Address)
    result = await db.execute(stmt)
    
    await db.commit()
    new_address = result.scalar_one_or_none()
    return new_address


#get all
async def get_all_addresses(db: AsyncSession, skip = 0, limit = 100):
    stmt = select(Address).offset(skip).limit(limit)
    result = await db.execute(stmt)
    addresses = result.scalars().all()
    return addresses

#get one
async def get_address(address_id: int, db: AsyncSession):
    stmt = select(Address).where(Address.id == address_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address {address_id} not found"
        )

    return address


#update
async def update_address(update_address: AddressUpdate, address_id: int, db: AsyncSession):
    stmt = select(Address).where(Address.id == address_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address {address_id} not found"
        )

    #updating values
    for k, v in update_address.model_dump().items():
        if v is not None:
            setattr(address, k, v)

    db.add(address)
    await db.commit()
    await db.refresh(address)
    return address
   


#delete
async def delete_address(address_id: int, db: AsyncSession):
    stmt = select(Address).where(Address.id == address_id)
    result = await db.execute(stmt)
    address = result.scalar_one_or_none

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address {address_id} not found"
        )
    
    await db.delete(address)
    await db.commit()
    return None