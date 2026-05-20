import datetime as dt
import database as db
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import ScalarResult
from typing import Annotated, List
from models import ConfirmedBooking
from datetime import date, time, datetime

async def check_overlap(bookings: List[ConfirmedBooking], s_time: Annotated[time, Body()], e_time: Annotated[time,Body()], date: Annotated[date, Body()]) -> bool: 
#bookings will be in date order, so only check those with the same date

    for b in bookings:
        if b.date < date:
            continue

        if b.date > date:
            break

        #end time between a start and end time
        if (e_time < b.end_time and e_time > b.start_time):
            return True
        
        #start time is between a start and end time
        if (s_time > b.start_time and s_time < b.end_time):
            return True 
        
        #entire booking is within another job timeframe
        if (s_time >= b.start_time and e_time <= b.end_time):
            return True

        #booking time is over an entire booking
        if(s_time <= b.start_time and e_time >= b.end_time):
            return True
    
    return False
