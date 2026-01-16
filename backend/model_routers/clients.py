from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from models import Client
from schemas import ClientCreate, ClientUpdate, ClientResponse
from model_crud import clients_crud as cc

router = APIRouter(prefix="/clients", tags=["Clients"])

#create
@router.post("/create", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client_endpoint(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    return await cc.create_client(client, db)

#get all
@router.get("/", response_model=List[ClientResponse])
async def get_all_clients_endpoint(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    return await cc.get_all_clients(db, skip, limit)


#get one
@router.get("/{client_id}", response_model=ClientResponse)
async def get_client_endpoint(client_id: int, db: AsyncSession = Depends(get_db)):
    return await cc.get_client(client_id, db)


#update
@router.patch("/update/{client_id}", response_model=ClientResponse,)
async def update_client_endpoint(up_client: ClientUpdate, client_id: int, db: AsyncSession = Depends(get_db)):
    return await cc.update_client(up_client, client_id, db)


#delete
@router.delete("/delete/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_endpoint(client_id: int, db: AsyncSession = Depends(get_db)):
    return await cc.delete_client(client_id, db)