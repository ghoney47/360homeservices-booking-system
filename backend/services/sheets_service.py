"""
Google Sheets service — primary data layer for customer bookings.

Authentication (set ONE of these env vars before starting the server):
  GOOGLE_CREDENTIALS_PATH  — absolute path to the service-account JSON key file
  GOOGLE_CREDENTIALS_JSON  — the full JSON content as a single-line string
                             (useful when you can't place files on the server)

Sheet: "Gavin's Schedule"  (ID: 1fiT_JuS_oiETo9J0M7X3_SsiqZrlpwBiYDPVd6eYHpA)
Worksheet tab: "Bookings"  (created automatically on first write if absent)

Column layout (A → P):
  A  Booking ID   — uuid4 string
  B  Client Name
  C  Phone
  D  Email
  E  Street #
  F  Street Name
  G  City
  H  State
  I  Zip
  J  Job Type     — e.g. "pwash"
  K  Date         — YYYY-MM-DD
  L  Start Time   — HH:MM:SS
  M  End Time     — HH:MM:SS
  N  Price ($)    — decimal dollars  (stored as a number so Sheets can sum/format it)
  O  Status       — "scheduled" | "in_process" | "completed" | "cancelled"
  P  Created At   — ISO-8601 UTC datetime
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date, datetime, time, timedelta

import gspread
from google.oauth2.service_account import Credentials

# ── Constants ──────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_ID       = "1fiT_JuS_oiETo9J0M7X3_SsiqZrlpwBiYDPVd6eYHpA"
WORKSHEET_NAME = "Bookings"

HEADERS = [
    "Booking ID", "Client Name", "Phone", "Email",
    "Street #", "Street Name", "City", "State", "Zip",
    "Job Type", "Date", "Start Time", "End Time",
    "Price ($)", "Status", "Created At",
]

_ACTIVE_STATUSES = {"scheduled", "in_process"}


# ── Auth helpers ───────────────────────────────────────────────────────────────

def _get_client() -> gspread.Client:
    """Return an authenticated gspread client.

    Credential resolution order:
      1. GOOGLE_CREDENTIALS_PATH  — path to service-account JSON file
      2. GOOGLE_CREDENTIALS_JSON  — raw JSON string as env var

    Raises:
        RuntimeError: neither credential source is configured.
    """
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if creds_path:
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    elif creds_json:
        info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        raise RuntimeError(
            "Google Sheets credentials not configured. "
            "Set GOOGLE_CREDENTIALS_PATH (path to JSON key file) "
            "or GOOGLE_CREDENTIALS_JSON (JSON content as string)."
        )

    return gspread.authorize(creds)


def _get_worksheet() -> gspread.Worksheet:
    """Return the Bookings worksheet, creating it with headers if it doesn't exist."""
    client = _get_client()
    spreadsheet = client.open_by_key(SHEET_ID)

    try:
        return spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=1000,
            cols=len(HEADERS),
        )
        ws.append_row(HEADERS, value_input_option="RAW")
        return ws


# ── Internal helpers ───────────────────────────────────────────────────────────

def _times_overlap(s1: time, e1: time, s2: time, e2: time) -> bool:
    """True if half-open intervals [s1, e1) and [s2, e2) overlap."""
    return s1 < e2 and e1 > s2


def _parse_time(val: str) -> time | None:
    try:
        return time.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None


def _parse_date(val: str) -> date | None:
    try:
        return date.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None


# ── Public read helpers ────────────────────────────────────────────────────────

def get_active_bookings_in_range(start: date, end: date) -> list[dict]:
    """Return active (scheduled / in_process) booking rows between start and end inclusive."""
    ws = _get_worksheet()
    rows = ws.get_all_records()  # list[dict] keyed by header names

    active: list[dict] = []
    for row in rows:
        status = str(row.get("Status", "")).lower()
        if status not in _ACTIVE_STATUSES:
            continue
        row_date = _parse_date(row.get("Date", ""))
        if row_date is None:
            continue
        if start <= row_date <= end:
            active.append(row)
    return active


def is_slot_available(target_date: date, start: time, end: time) -> bool:
    """Return True if no active booking conflicts with the given window on target_date."""
    bookings = get_active_bookings_in_range(target_date, target_date)
    for b in bookings:
        b_start = _parse_time(b.get("Start Time", ""))
        b_end   = _parse_time(b.get("End Time", ""))
        if b_start is None or b_end is None:
            continue
        if _times_overlap(start, end, b_start, b_end):
            return False
    return True


def get_openings(
    duration: int,
    start_date: date,
    op_start: time,
    op_end: time,
    dead_start: time,
    dead_end: time,
    max_slots: int = 16,
    max_search_days: int = 90,
) -> list[datetime]:
    """Return up to max_slots available start datetimes for a job of the given duration (minutes).

    Mirrors the logic in services/availability_service.py but reads from Sheets
    instead of the database.
    """
    search_end = start_date + timedelta(days=14)
    booked_rows = get_active_bookings_in_range(start_date, search_end)

    def _day_slots(d: date) -> list[tuple[time, time]]:
        result = []
        for row in booked_rows:
            if _parse_date(row.get("Date", "")) != d:
                continue
            bs = _parse_time(row.get("Start Time", ""))
            be = _parse_time(row.get("End Time", ""))
            if bs and be:
                result.append((bs, be))
        return result

    openings: list[datetime] = []
    current  = start_date
    deadline = start_date + timedelta(days=max_search_days)

    while len(openings) < max_slots and current <= deadline:
        # Expand the cached window as we move forward
        if current > search_end:
            search_end  = current + timedelta(days=14)
            booked_rows = get_active_bookings_in_range(current, search_end)

        day_booked = _day_slots(current)

        for hour in range(24):
            if time(hour, 0) < op_start:
                continue
            if time(hour, 0) >= op_end:
                break

            minute = 0
            while minute < 60:
                slot_s      = time(hour, minute)
                slot_start  = datetime.combine(current, slot_s)
                slot_end    = slot_start + timedelta(minutes=duration)

                if slot_end.date() != current:
                    break

                slot_e = slot_end.time()

                if slot_e > op_end:
                    minute += duration
                    continue

                in_dead  = _times_overlap(slot_s, slot_e, dead_start, dead_end)
                conflict = any(_times_overlap(slot_s, slot_e, bs, be) for bs, be in day_booked)

                if not in_dead and not conflict:
                    openings.append(slot_start)

                minute += duration
                if len(openings) >= max_slots:
                    break

            if len(openings) >= max_slots:
                break

        current += timedelta(days=1)

    return openings


# ── Public write helper ────────────────────────────────────────────────────────

def append_booking(
    *,
    client_name: str,
    phone: str,
    email: str,
    street_number: str,
    street_name: str,
    city: str,
    state: str,
    zip_code: str,
    job_type: str,
    booking_date: date,
    start_time: time,
    end_time: time,
    price_cents: int,
) -> str:
    """Append a new booking row to the Sheets worksheet.

    Returns the generated booking_id (uuid4 string).
    """
    booking_id = str(uuid.uuid4())
    ws = _get_worksheet()

    ws.append_row(
        [
            booking_id,
            client_name,
            phone,
            email,
            street_number,
            street_name,
            city,
            state,
            zip_code,
            job_type,
            str(booking_date),                          # YYYY-MM-DD
            str(start_time),                            # HH:MM:SS
            str(end_time),                              # HH:MM:SS
            round(price_cents / 100, 2),                # dollars (Sheets number)
            "scheduled",
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
        ],
        value_input_option="USER_ENTERED",
    )

    return booking_id
