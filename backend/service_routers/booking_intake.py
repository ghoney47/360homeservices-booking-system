"""
Customer-facing booking intake router — backed by Google Sheets.

Endpoints
---------
GET  /api/v1/intake/openings   — available time slots (reads from Sheets)
POST /api/v1/intake/book       — create a booking    (writes to Sheets)

These replace the old three-step flow:
  POST /api/v1/addresses/create
  POST /api/v1/clients/create
  POST /api/v1/bookings/create

The old DB-backed routes are still registered and untouched so the
project can pivot back to Postgres/SQLite at any time.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List

from fastapi import APIRouter, HTTPException, Request, status

from limiter import limiter
from schemas_intake import IntakeBookingRequest, IntakeBookingResponse
from services import sheets_service as ss

router = APIRouter(prefix="/intake", tags=["Booking Intake (Sheets)"])


@router.get("/openings", response_model=List[datetime])
def get_openings_endpoint(
    duration:   int,
    start_date: date,
    op_start:   time,
    op_end:     time,
    dead_start: time,
    dead_end:   time,
):
    """Return up to 16 available booking start-times from Google Sheets.

    Query params match the existing /bookings/openings signature so the
    frontend needs only a URL swap.
    """
    try:
        return ss.get_openings(
            duration=duration,
            start_date=start_date,
            op_start=op_start,
            op_end=op_end,
            dead_start=dead_start,
            dead_end=dead_end,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )


@router.post("/book", response_model=IntakeBookingResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_booking_endpoint(request: Request, payload: IntakeBookingRequest):
    """Check slot availability and write a new booking row to Google Sheets."""
    try:
        # Double-check availability server-side (the frontend already showed
        # available slots, but race conditions are possible)
        if not ss.is_slot_available(payload.date, payload.start_time, payload.end_time):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"The slot {payload.start_time}–{payload.end_time} "
                    f"on {payload.date} was just taken. Please pick another time."
                ),
            )

        booking_id = ss.append_booking(
            client_name=payload.name,
            phone=payload.phone,
            email=payload.email,
            street_number=payload.street_number,
            street_name=payload.street_name,
            city=payload.city,
            state=payload.state,
            zip_code=payload.zip_code,
            job_type=payload.job_type,
            booking_date=payload.date,
            start_time=payload.start_time,
            end_time=payload.end_time,
            price_cents=payload.price_cents,
        )

        return IntakeBookingResponse(
            booking_id=booking_id,
            message="Booking confirmed! We'll be in touch to confirm details.",
        )

    except HTTPException:
        raise  # re-raise 409 as-is

    except RuntimeError as exc:
        # Sheets credentials missing / API unreachable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
