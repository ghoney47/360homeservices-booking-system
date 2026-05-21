"""
Pydantic schemas for the customer-facing booking intake endpoints.

These live separately from schemas.py so the DB-backed schemas stay
untouched and can be restored easily if the project pivots back.
"""

from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, EmailStr, Field, field_validator

from utils import validators as val


class IntakeBookingRequest(BaseModel):
    """Single payload that replaces the old 3-step address → client → booking flow."""

    # Contact info
    name:  str      = Field(max_length=50)
    phone: str      = Field(max_length=15)
    email: EmailStr = Field(max_length=50)

    # Service address
    street_number: str = Field(max_length=10)
    street_name:   str = Field(max_length=50)
    city:          str = Field(max_length=20)
    state:         str = Field(max_length=2)
    zip_code:      str = Field(max_length=5)

    # Booking
    job_type:    str  = Field(max_length=30)
    date:        date
    start_time:  time
    end_time:    time
    price_cents: int

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return val.validate_phone_number(v)

    @field_validator("price_cents")
    @classmethod
    def validate_price(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("price_cents must be a positive integer")
        return v

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, end: time, info) -> time:
        start = info.data.get("start_time")
        if start is not None and end <= start:
            raise ValueError("end_time must be after start_time")
        return end


class IntakeBookingResponse(BaseModel):
    booking_id: str
    message:    str
