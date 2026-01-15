from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from models import Client
from schemas import ClientCreate, ClientUpdate, ClientResponse
from model_crud import clients_crud as cc

router = APIRouter(prefix="/clients", tags=["Clients"])

#create

    


#get all


#get one


#update


#delete