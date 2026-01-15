from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from models import Client
from schemas import ClientCreate, ClientUpdate, ClientResponse
from model_crud import clients_crud as cc

router = APIRouter(prefix="/clients", tags=["Clients"])

#create
@router.post("/create")
async def create_client_endpoint(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    return cc.create_client(client, db)

#get all
@router.get("/")
async def get_all_clients_endpoint(db: AsyncSession = Depends(get_db), skip = 0, limit = 100):
    return cc.get_all_clients(db, skip, limit)


#get one
@router.get("/{client_id}")
async def get_client_endpoint(client_id: int, db: AsyncSession = Depends(get_db)):
    return cc.get_client(client_id, db)


#update
@router.patch("/update/{client_id}")
async def update_client_endpoint(up_client: ClientUpdate, client_id: int, db: AsyncSession = Depends(get_db)):
    return cc.update_client(up_client, client_id, db)


#delete
@router.delete("/delete/{client_id}")
async def delete_client_endpoint(client_id: int, db: AsyncSession = Depends(get_db)):
    return cc.delete_client(client_id, db)