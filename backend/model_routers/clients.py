from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import Client
from schemas import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter(prefix="/clients", tags=["Clients"])

#create
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    stmt = insert(Client).values(**client.model_dump()).returning(Client)
    result = await db.execute(stmt)

    await db.commit()
    new_client = result.scalar_one_or_none()
    return new_client
    
    


#get all


#get one


#update


#delete