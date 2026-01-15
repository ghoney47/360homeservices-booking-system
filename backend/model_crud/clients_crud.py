from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import Client
from schemas import ClientCreate, ClientUpdate, ClientResponse
from utils.validators import address_exists
from addresses_crud import create_address

#create
async def create_client(client: ClientCreate, db: AsyncSession):
    
    address_id = client.address_id

    #determining if address exists
    if not await address_exists(client.address_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address {address_id} does not exist"
        )


    stmt = insert(Client).values(**client.model_dump()).returning(Client)
    result = await db.execute(stmt)

    await db.commit()

    new_client = result.scalar_one_or_none()
    return new_client

#get all
async def get_all_clients(db: AsyncSession, skip = 0, limit = 100):
    stmt = select(Client).offset(skip).limit(limit)
    result = await db.execute(stmt)
    clients = result.scalars().all()
    return clients

#get one
async def get_client(client_id: int, db: AsyncSession):
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} does not exist"
        )
    
    return client

#update
async def update_client(update_client: ClientUpdate, client_id: int, db: AsyncSession):
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} does not exist"
        )
    
    #updating attributes
    for k, v in update_client.model_dump().items():
        setattr(client, k, v)

    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client

#delete
async def delete_client(client_id: int, db: AsyncSession):
    stmt = select(Client).where(Client.id == client_id)
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {client_id} does not exist"
        )
    
    await db.delete(client)
    await db.commit()
    return None


