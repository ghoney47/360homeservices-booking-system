from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import Address
from schemas import AddressCreate, AddressResponse, AddressUpdate

#create
async def create_address(address: AddressCreate, db: AsyncSession):
    """creates address object

    Args:
        address (AddressCreate): create schema
        db (AsyncSession): database connection

    Returns:
        Address: new address object
    """
    stmt = insert(Address).values(**address.model_dump()).returning(Address)
    result = await db.execute(stmt)
    
    await db.commit()
    new_address = result.scalar_one_or_none()
    return new_address


#get all
async def get_all_addresses(db: AsyncSession, skip: int, limit: int):
    """get all addresses held in the database

    Args:
        db (AsyncSession): database connection
        skip (int): rows skipped
        limit (int): rows shown

    Returns:
        list[Address]: list of all address objects 
    """
    stmt = select(Address).offset(skip).limit(limit)
    result = await db.execute(stmt)
    addresses = result.scalars().all()
    return addresses

#get one
async def get_address(address_id: int, db: AsyncSession):
    """get address based on address_id

    Args:
        address_id (int): address id
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if address is not found

    Returns:
        Address: specified address 
    """
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
    """update a given address

    Args:
        update_address (AddressUpdate): Update schema
        address_id (int): address id 
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if address is not found

    Returns:
        Address: updated address
    """
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
    """delete a specified address

    Args:
        address_id (int): address id
        db (AsyncSession): database connection

    Raises:
        HTTPException: raises 404 if address is not found

    Returns:
        None
    """
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