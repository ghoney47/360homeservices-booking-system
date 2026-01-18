from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import Address
from schemas import AddressCreate, AddressResponse, AddressUpdate
from model_crud import addresses_crud as ac

router = APIRouter(prefix="/addresses", tags=["Addresses"])

#create
@router.post("/create", response_model= AddressResponse)
async def create_address_endpoint(address: AddressCreate, db: AsyncSession = Depends(get_db)):
    return await ac.create_address(address, db)

#get all
@router.get("/", response_model=List[AddressResponse])
async def get_all_addresses_endpoint(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    return await ac.get_all_addresses(db, skip, limit)

#get one
@router.get("/{address_id}", response_model=AddressResponse)
async def get_address_endpoint(address_id: int, db: AsyncSession = Depends(get_db)):
    return await ac.get_address(address_id, db)

#update
@router.patch("/update/{address_id}", response_model = AddressResponse)
async def update_address_endpoint(up_address: AddressUpdate, address_id: int, db: AsyncSession = Depends(get_db)):
    return await ac.update_address(up_address, address_id, db)

#delete
@router.delete("/delete/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address_endpoint(address_id: int, db: AsyncSession = Depends(get_db)):
    return await ac.delete_address(address_id, db)
