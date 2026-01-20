from database import get_db
from fastapi import HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert, ScalarResult
import sqlalchemy as sa
from datetime import date, time, datetime, timedelta
from typing import List, Annotated, Optional
from utils.date_helpers import check_overlap
from models import ConfirmedBooking



async def get_booking_within_dates(s_date: Annotated[date, Body()], e_date: Annotated[date, Body()], db: AsyncSession) -> List[ConfirmedBooking]:
    """Gets all bookings within a certain span of time

    Args:
        s_date (dt.date): start date
        e_date (_type_): end date
        db (AsyncSession): database connection

    Returns:
        List[ConfirmedBooking]: list of confirmed booking objects within the date period
    """
    stmt = select(ConfirmedBooking).where((ConfirmedBooking.date >= s_date) & 
                                            (ConfirmedBooking.date <= e_date)) #TODO check logic here
    result = await db.execute(stmt)
    bookings = list(result.scalars().all())

    return bookings



async def get_openings(duration: int, s_date: Annotated[date, Body()], op_start: Annotated[time, Body()], op_end: Annotated[time, Body()], dead_hours_s: Annotated[time, Body()], dead_hours_e: Annotated[time, Body()], db: AsyncSession) -> List[datetime]:
    """
    Get a list of potential start times for a job

    Args:
        duration (int): minutes job will take
        s_date (Annotated[date, Body): start of search date
        op_start (Annotated[time, Body): operation hour start
        op_end (Annotated[time, Body): operation hour end
        dead_hours_s (Annotated[time, Body): dead hour start
        dead_hours_e (Annotated[time, Body): dead hour end
        db (AsyncSession): database connection

    Returns:
        List[datetime]: _description_
    """
    two_weeks_later = s_date + timedelta(days=14)

    #finding bookings for the next two weeks from start
    filled_slots = await get_booking_within_dates(s_date, two_weeks_later, db) #need to do like 3 weeks past start date or smth

    out = []

    curr_date = s_date

    #will find next 16 open slots
    while len(out) < 16:
            
        for h in range(24):

            curr_time = time(h, 0)

            #skips iterations before operation hours
            if curr_time < op_start:
                continue

            #moves to the next day if after operation hours 
            if curr_time > op_end:
                break
            
            m = 0

            while m < 60:
                trial_time = time(h, m)
                s_dt = datetime.combine(curr_date, trial_time)
                e_dt = s_dt + timedelta(minutes=duration)

                #drops out of loop if book spans overnight
                if e_dt.date() != curr_date:
                    break

                #checks if ending is within hours of operations
                if e_dt.time() > op_end:
                    m += duration
                    continue

                #adds to list if there is no overlap, and does not fall withiin dead hours
                if not await check_overlap(filled_slots, s_dt.time(), e_dt.time(), curr_date):
                    if e_dt.time() <= dead_hours_s or s_dt.time() >= dead_hours_e:
                        out.append(s_dt)

                m += duration

                #checks output numbers every iteration
                if len(out) > 16:
                    break
            
            #checks output numbers every iteration
            if len(out) > 16:
                break


        
        #moves to the next day
        curr_date += timedelta(days=1)
    
    return out





        

    
    

