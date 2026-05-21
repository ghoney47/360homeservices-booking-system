import uuid
from datetime import date, time, datetime, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import ConfirmedBooking, BookingStatus, Employee
from schemas import ConfirmedBookingCreate
from utils.validators import client_exists, address_exists

# Max days forward get_openings will search before giving up
_MAX_SEARCH_DAYS = 90


def _times_overlap(s1: time, e1: time, s2: time, e2: time) -> bool:
    """True if the half-open interval [s1, e1) overlaps [s2, e2)."""
    return s1 < e2 and e1 > s2


def _active_statuses():
    return [BookingStatus.SCHEDULED, BookingStatus.IN_PROCESS]


async def _bookings_on_date(target: date, db: AsyncSession) -> List[ConfirmedBooking]:
    """Active (non-cancelled, non-completed) bookings on a given date."""
    stmt = (
        select(ConfirmedBooking)
        .where(
            ConfirmedBooking.date == target,
            ConfirmedBooking.status.in_(_active_statuses()),
        )
        .order_by(ConfirmedBooking.start_time)
    )
    return list((await db.execute(stmt)).scalars().all())


async def _bookings_within_dates(start: date, end: date, db: AsyncSession) -> List[ConfirmedBooking]:
    """Active bookings within a date range."""
    stmt = (
        select(ConfirmedBooking)
        .where(
            ConfirmedBooking.date >= start,
            ConfirmedBooking.date <= end,
            ConfirmedBooking.status.in_(_active_statuses()),
        )
        .order_by(ConfirmedBooking.date, ConfirmedBooking.start_time)
    )
    return list((await db.execute(stmt)).scalars().all())


async def is_slot_available(target_date: date, start_time: time, end_time: time, db: AsyncSession) -> bool:
    """Return True if no active booking overlaps the requested window on target_date."""
    bookings = await _bookings_on_date(target_date, db)
    return not any(_times_overlap(start_time, end_time, b.start_time, b.end_time) for b in bookings)


async def get_openings(
    duration: int,
    start_date: date,
    op_start: time,
    op_end: time,
    dead_start: time,
    dead_end: time,
    db: AsyncSession,
) -> List[datetime]:
    """Return the next 16 available start times for a job of the given duration (minutes).

    Args:
        duration:   Job length in minutes.
        start_date: Earliest date to consider.
        op_start:   Start of operating hours.
        op_end:     End of operating hours.
        dead_start: Start of the dead-hour window (no slots begin or overlap here).
        dead_end:   End of the dead-hour window.
    """
    search_end = start_date + timedelta(days=14)
    booked = await _bookings_within_dates(start_date, search_end, db)

    openings: List[datetime] = []
    current_date = start_date
    deadline = start_date + timedelta(days=_MAX_SEARCH_DAYS)

    while len(openings) < 16:
        if current_date > deadline:
            break  # no openings found within the search window

        # Expand the cached booking list when we move past the initial window
        if current_date > search_end:
            search_end = current_date + timedelta(days=14)
            booked = await _bookings_within_dates(current_date, search_end, db)

        day_bookings = [b for b in booked if b.date == current_date]

        for hour in range(24):
            if time(hour, 0) < op_start:
                continue
            if time(hour, 0) >= op_end:
                break

            minute = 0
            while minute < 60:
                slot_s = time(hour, minute)
                slot_start_dt = datetime.combine(current_date, slot_s)
                slot_end_dt = slot_start_dt + timedelta(minutes=duration)

                if slot_end_dt.date() != current_date:
                    break

                slot_e = slot_end_dt.time()

                if slot_e > op_end:
                    minute += duration
                    continue

                in_dead = _times_overlap(slot_s, slot_e, dead_start, dead_end)
                conflict = any(_times_overlap(slot_s, slot_e, b.start_time, b.end_time) for b in day_bookings)

                if not conflict and not in_dead:
                    openings.append(slot_start_dt)

                minute += duration
                if len(openings) >= 16:
                    break

            if len(openings) >= 16:
                break

        current_date += timedelta(days=1)

    return openings


async def book_slot(booking: ConfirmedBookingCreate, db: AsyncSession) -> ConfirmedBooking:
    """Validate availability and create a confirmed booking.

    Raises:
        HTTP 404: client, address, or an employee ID not found.
        HTTP 409: the requested time slot conflicts with an existing booking.
        HTTP 422: start_time is not before end_time.
    """
    if not await client_exists(booking.client_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {booking.client_id} not found",
        )

    if not await address_exists(booking.address_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address {booking.address_id} not found",
        )

    if booking.start_time >= booking.end_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_time must be before end_time",
        )

    if not await is_slot_available(booking.date, booking.start_time, booking.end_time, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot {booking.start_time}–{booking.end_time} on {booking.date} is already booked",
        )

    # Resolve employees, validating each ID
    employees: List[Employee] = []
    for eid in booking.assigned_employees:
        emp = await db.get(Employee, eid)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {eid} not found",
            )
        employees.append(emp)

    # assigned_employees is an M2M relationship, not a column — exclude it from the row data
    row_data = booking.model_dump(exclude={"assigned_employees"})
    row_data["id_hash"] = str(uuid.uuid4())

    new_booking = ConfirmedBooking(**row_data)
    new_booking.assigned_employees = employees

    db.add(new_booking)
    await db.commit()

    # Reload with relationships eager-loaded for the response
    stmt = (
        select(ConfirmedBooking)
        .options(
            selectinload(ConfirmedBooking.assigned_employees),
            selectinload(ConfirmedBooking.address),
            selectinload(ConfirmedBooking.client),
        )
        .where(ConfirmedBooking.id_hash == new_booking.id_hash)
    )
    return (await db.execute(stmt)).scalar_one()
