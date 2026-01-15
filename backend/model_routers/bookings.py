from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from typing import List
from database import get_db
from models import ConfirmedBooking
from schemas import ConfirmedBookingCreate, ConfirmedBookingUpdate, ConfirmedBookingResponse