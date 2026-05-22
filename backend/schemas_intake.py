"""
Pydantic schemas for the customer-facing booking intake endpoints.

These live separately from schemas.py so the DB-backed schemas stay
untouched and can be restored easily if the project pivots back.
"""

from __future__ import annotations

from datetime import date, time

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from utils import validators as val


class IntakeBookingRequest(BaseModel):
    """Single payload that replaces the old 3-step address → client → booking flow."""

    # Contact info
    name:  str      = Field(min_length=2, max_length=50)
    phone: str      = Field(max_length=15)
    email: EmailStr = Field(max_length=50)

    # Service address
    street_number: str = Field(min_length=1, max_length=10)
    street_name:   str = Field(min_length=2, max_length=50)
    city:          str = Field(min_length=2, max_length=20)
    state:         str = Field(min_length=2, max_length=2)
    zip_code:      str = Field(min_length=5, max_length=5)

    # Booking
    job_type:    str  = Field(max_length=30)
    date:        date
    start_time:  time
    end_time:    time
    price_cents: int

    # ── Field validators ───────────────────────────────────────────────────────

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 2:
            raise ValueError("Name must be at least 2 characters")
        return stripped

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return val.validate_phone_number(v)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        return val.validate_state(v)

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        return val.validate_zip_code(v)

    @field_validator("job_type")
    @classmethod
    def validate_job_type(cls, v: str) -> str:
        return val.validate_job_type(v)

    @field_validator("date")
    @classmethod
    def date_not_in_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Booking date cannot be in the past")
        return v

    @field_validator("price_cents")
    @classmethod
    def validate_price(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("price_cents must be a positive integer")
        if v > 1_000_000_00:  # $100,000 ceiling — catches runaway values
            raise ValueError("price_cents exceeds maximum allowed value")
        return v

    # ── Cross-field validators ─────────────────────────────────────────────────

    @model_validator(mode="after")
    def end_after_start(self) -> "IntakeBookingRequest":
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time must be after start_time")
        return self


class IntakeBookingResponse(BaseModel):
    booking_id: str
    message:    str
