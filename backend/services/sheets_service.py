"""
Google Sheets service — primary data layer for customer bookings.

Authentication — OAuth2 (no service-account key required):

  LOCAL DEV
    1. Set GOOGLE_CREDENTIALS_PATH to the credentials.json downloaded from
       Google Cloud Console (OAuth 2.0 Client ID, Desktop app type).
    2. On first run the server will open a browser tab to authorise access.
    3. After approval a token is saved to GOOGLE_TOKEN_PATH (default: token.json
       next to credentials.json). Subsequent runs use the saved token silently.

  PRODUCTION (no browser available)
    After completing the local dev flow once, copy the contents of the saved
    token file and set GOOGLE_TOKEN_JSON to that JSON string in your host's
    environment variables dashboard. The app will use the refresh token
    automatically — no browser needed.

Sheet: "Gavin's Schedule"  (ID: 1fiT_JuS_oiETo9J0M7X3_SsiqZrlpwBiYDPVd6eYHpA)
Worksheet tabs:
  "Bookings"       — created automatically on first write if absent
  "Blackout Dates" — created automatically on first read if absent

Bookings column layout (A → P):
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

Blackout Dates column layout (A → B):
  A  Date         — YYYY-MM-DD  (required)
  B  Reason       — free text   (optional, for reference only)
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date, datetime, time, timedelta, timezone

UTC = timezone.utc

import gspread

# ── Constants ──────────────────────────────────────────────────────────────────

# gspread's standard OAuth scopes — required for spreadsheet read/write
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

SHEET_ID              = os.getenv("GOOGLE_SHEET_ID", "1fiT_JuS_oiETo9J0M7X3_SsiqZrlpwBiYDPVd6eYHpA")
WORKSHEET_NAME        = "Bookings"
BLACKOUT_WORKSHEET    = "Blackout Dates"

HEADERS = [
    "Booking ID", "Client Name", "Phone", "Email",
    "Street #", "Street Name", "City", "State", "Zip",
    "Job Type", "Date", "Start Time", "End Time",
    "Price ($)", "Status", "Created At",
]

BLACKOUT_HEADERS = ["Date", "Reason"]

_ACTIVE_STATUSES = {"scheduled", "in_process"}

# ── Recurring blackout weekdays ────────────────────────────────────────────────
# Add weekday numbers here to close those days every week.
# Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
# e.g. every Sunday closed → {6}  |  weekends closed → {5, 6}
BLACKOUT_WEEKDAYS: set[int] = set()  # ← ADD RECURRING CLOSED DAYS HERE


# ── Auth helpers ───────────────────────────────────────────────────────────────

def _get_client() -> gspread.Client:
    """Return an authenticated gspread client via OAuth2.

    Resolution order:
      1. GOOGLE_TOKEN_JSON  — production: full token JSON as an env-var string
      2. GOOGLE_CREDENTIALS_PATH + GOOGLE_TOKEN_PATH — local dev browser flow

    Raises:
        RuntimeError: credentials not configured.
    """
    # ── Production path: token JSON stored as env var ──────────────────────────
    token_json = os.getenv("GOOGLE_TOKEN_JSON")
    if token_json:
        from google.oauth2.credentials import Credentials as UserCredentials
        from google.auth.transport.requests import Request

        info  = json.loads(token_json)
        creds = UserCredentials.from_authorized_user_info(info, SCOPES)

        # Refresh silently if the access token has expired (refresh token handles it)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return gspread.authorize(creds)

    # ── Local dev path: browser-based OAuth flow ───────────────────────────────
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if not creds_path:
        raise RuntimeError(
            "Google Sheets credentials not configured.\n"
            "  Local dev  → set GOOGLE_CREDENTIALS_PATH to your credentials.json\n"
            "  Production → set GOOGLE_TOKEN_JSON to the contents of your token file"
        )

    token_path = os.getenv(
        "GOOGLE_TOKEN_PATH",
        os.path.join(os.path.dirname(creds_path), "token.json"),
    )

    return gspread.oauth(
        credentials_filename=creds_path,
        authorized_user_filename=token_path,
    )


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


def _get_blackout_worksheet() -> gspread.Worksheet:
    """Return the Blackout Dates worksheet, creating it with headers if it doesn't exist."""
    client = _get_client()
    spreadsheet = client.open_by_key(SHEET_ID)

    try:
        return spreadsheet.worksheet(BLACKOUT_WORKSHEET)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(
            title=BLACKOUT_WORKSHEET,
            rows=200,
            cols=len(BLACKOUT_HEADERS),
        )
        ws.append_row(BLACKOUT_HEADERS, value_input_option="RAW")
        return ws


def get_blackout_dates(start: date, end: date) -> set[date]:
    """Return the set of blacked-out dates between start and end (inclusive).

    Combines two sources:
      1. BLACKOUT_WEEKDAYS — recurring weekday closures (hardcoded above).
      2. The "Blackout Dates" Google Sheet tab — one-off dates (holidays, etc.).
    """
    blacked_out: set[date] = set()

    # ── Recurring weekday closures ─────────────────────────────────────────────
    if BLACKOUT_WEEKDAYS:
        current = start
        while current <= end:
            if current.weekday() in BLACKOUT_WEEKDAYS:
                blacked_out.add(current)
            current += timedelta(days=1)

    # ── One-off Sheet dates ────────────────────────────────────────────────────
    ws = _get_blackout_worksheet()
    rows = ws.get_all_records()   # list[dict] keyed by "Date" / "Reason"
    for row in rows:
        d = _parse_date(row.get("Date", ""))
        if d is not None and start <= d <= end:
            blacked_out.add(d)

    return blacked_out


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
    """Return True if the slot is available: the day is not blacked out and no
    active booking conflicts with the requested window."""
    # Check blackout first (cheaper than a full Sheets read)
    if target_date.weekday() in BLACKOUT_WEEKDAYS:
        return False
    blacked_out = get_blackout_dates(target_date, target_date)
    if target_date in blacked_out:
        return False

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

    openings:    list[datetime] = []
    current      = start_date
    deadline     = start_date + timedelta(days=max_search_days)
    blacked_out  = get_blackout_dates(start_date, deadline)

    while len(openings) < max_slots and current <= deadline:
        # Expand the cached window as we move forward
        if current > search_end:
            search_end  = current + timedelta(days=14)
            booked_rows = get_active_bookings_in_range(current, search_end)

        # Skip days that are fully blacked out
        if current in blacked_out:
            current += timedelta(days=1)
            continue

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
            datetime.now(UTC).isoformat(timespec="seconds"),
        ],
        value_input_option="USER_ENTERED",
    )

    return booking_id
