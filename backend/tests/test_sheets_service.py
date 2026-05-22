"""
Tests for services/sheets_service.py

Unit tests  — mock out gspread; test pure logic only.
Integration — actually read/write the live "Gavin's Schedule" sheet.
              These are skipped automatically if credentials aren't configured.
"""

import os
import sys
from datetime import date, datetime, time, timedelta
from unittest.mock import MagicMock, patch

import pytest

# Make sure backend/ is on the path when running from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

import services.sheets_service as ss


# ── Helpers ────────────────────────────────────────────────────────────────────

def _has_credentials() -> bool:
    return bool(os.getenv("GOOGLE_CREDENTIALS_PATH") or os.getenv("GOOGLE_TOKEN_JSON"))

requires_credentials = pytest.mark.skipif(
    not _has_credentials(),
    reason="Google credentials not configured — skipping integration tests",
)


# ── Unit tests: _times_overlap ─────────────────────────────────────────────────

class TestTimesOverlap:
    def test_clear_overlap(self):
        assert ss._times_overlap(time(9, 0), time(11, 0), time(10, 0), time(12, 0))

    def test_no_overlap_before(self):
        assert not ss._times_overlap(time(8, 0), time(9, 0), time(9, 0), time(10, 0))

    def test_no_overlap_after(self):
        assert not ss._times_overlap(time(10, 0), time(11, 0), time(8, 0), time(9, 0))

    def test_contained_within(self):
        assert ss._times_overlap(time(9, 0), time(11, 0), time(9, 30), time(10, 30))

    def test_exact_boundary_no_overlap(self):
        # Half-open intervals: [9,11) and [11,13) do NOT overlap
        assert not ss._times_overlap(time(9, 0), time(11, 0), time(11, 0), time(13, 0))


# ── Unit tests: is_slot_available ─────────────────────────────────────────────

class TestIsSlotAvailable:
    def _make_booking(self, start: str, end: str, status="scheduled"):
        return {"Date": "2026-06-01", "Start Time": start, "End Time": end, "Status": status}

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_available_when_no_bookings(self, mock_get):
        mock_get.return_value = []
        assert ss.is_slot_available(date(2026, 6, 1), time(9, 0), time(11, 0))

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_unavailable_when_overlap(self, mock_get):
        mock_get.return_value = [self._make_booking("10:00:00", "12:00:00")]
        assert not ss.is_slot_available(date(2026, 6, 1), time(9, 0), time(11, 0))

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_available_adjacent_slot(self, mock_get):
        mock_get.return_value = [self._make_booking("11:00:00", "13:00:00")]
        assert ss.is_slot_available(date(2026, 6, 1), time(9, 0), time(11, 0))

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_cancelled_booking_does_not_block(self, mock_get):
        # Cancelled bookings are excluded by get_active_bookings_in_range already;
        # simulate that by returning an empty list (active filter already applied)
        mock_get.return_value = []
        assert ss.is_slot_available(date(2026, 6, 1), time(9, 0), time(11, 0))


# ── Unit tests: get_openings ───────────────────────────────────────────────────

class TestGetOpenings:
    OP_START   = time(8, 0)
    OP_END     = time(17, 0)
    DEAD_START = time(12, 0)
    DEAD_END   = time(13, 0)
    DURATION   = 120  # 2 hours

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_returns_up_to_16_slots(self, mock_get):
        mock_get.return_value = []
        slots = ss.get_openings(
            self.DURATION, date(2026, 6, 1),
            self.OP_START, self.OP_END,
            self.DEAD_START, self.DEAD_END,
        )
        assert len(slots) == 16

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_slots_are_datetimes(self, mock_get):
        mock_get.return_value = []
        slots = ss.get_openings(
            self.DURATION, date(2026, 6, 1),
            self.OP_START, self.OP_END,
            self.DEAD_START, self.DEAD_END,
        )
        assert all(isinstance(s, datetime) for s in slots)

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_no_slots_in_dead_window(self, mock_get):
        mock_get.return_value = []
        slots = ss.get_openings(
            self.DURATION, date(2026, 6, 1),
            self.OP_START, self.OP_END,
            self.DEAD_START, self.DEAD_END,
        )
        for slot in slots:
            slot_end = (datetime.combine(slot.date(), slot.time()) + timedelta(minutes=self.DURATION)).time()
            assert not ss._times_overlap(slot.time(), slot_end, self.DEAD_START, self.DEAD_END), (
                f"Slot {slot.time()}–{slot_end} overlaps the dead window"
            )

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_slots_within_operating_hours(self, mock_get):
        mock_get.return_value = []
        slots = ss.get_openings(
            self.DURATION, date(2026, 6, 1),
            self.OP_START, self.OP_END,
            self.DEAD_START, self.DEAD_END,
        )
        for slot in slots:
            slot_end = (datetime.combine(slot.date(), slot.time()) + timedelta(minutes=self.DURATION)).time()
            assert slot.time() >= self.OP_START
            assert slot_end <= self.OP_END


# ── Unit tests: intake API endpoints ──────────────────────────────────────────

class TestIntakeEndpoints:
    """Test the FastAPI intake router with the Sheets layer mocked out."""

    @pytest.fixture(autouse=True)
    def client(self):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from service_routers.booking_intake import router
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        self.client = TestClient(app)

    @patch("services.sheets_service.get_active_bookings_in_range")
    def test_openings_returns_list(self, mock_get):
        mock_get.return_value = []
        resp = self.client.get("/api/v1/intake/openings", params={
            "duration": 120,
            "start_date": "2026-06-01",
            "op_start": "08:00:00",
            "op_end": "17:00:00",
            "dead_start": "12:00:00",
            "dead_end": "13:00:00",
        })
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) > 0

    @patch("services.sheets_service.append_booking", return_value="test-uuid-1234")
    @patch("services.sheets_service.is_slot_available", return_value=True)
    def test_book_success(self, mock_avail, mock_append):
        resp = self.client.post("/api/v1/intake/book", json={
            "name": "Jane Smith",
            "phone": "+14042345678",
            "email": "jane@example.com",
            "street_number": "123",
            "street_name": "Maple Ave",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "job_type": "pwash",
            "date": "2026-06-01",
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "price_cents": 15000,
        })
        assert resp.status_code == 201
        assert resp.json()["booking_id"] == "test-uuid-1234"

    @patch("services.sheets_service.is_slot_available", return_value=False)
    def test_book_conflict(self, mock_avail):
        resp = self.client.post("/api/v1/intake/book", json={
            "name": "Jane Smith",
            "phone": "+14042345678",
            "email": "jane@example.com",
            "street_number": "123",
            "street_name": "Maple Ave",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "job_type": "pwash",
            "date": "2026-06-01",
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "price_cents": 15000,
        })
        assert resp.status_code == 409

    def test_book_invalid_payload(self):
        resp = self.client.post("/api/v1/intake/book", json={"name": "incomplete"})
        assert resp.status_code == 422


# ── Integration tests: live Google Sheet ──────────────────────────────────────

@requires_credentials
class TestSheetsIntegration:
    """Write and read a real row on Gavin's Schedule → Bookings tab."""

    TEST_NAME = "__pytest_integration_test__"

    def test_append_and_verify(self):
        booking_id = ss.append_booking(
            client_name=self.TEST_NAME,
            phone="000-000-0000",
            email="test@pytest.local",
            street_number="1",
            street_name="Test St",
            city="Testville",
            state="IL",
            zip_code="00000",
            job_type="pytest",
            booking_date=date(2099, 1, 1),
            start_time=time(9, 0),
            end_time=time(11, 0),
            price_cents=100,
        )
        assert booking_id  # got a uuid back

        # Read it back
        ws   = ss._get_worksheet()
        rows = ws.get_all_records()
        match = [r for r in rows if r.get("Booking ID") == booking_id]
        assert len(match) == 1
        assert match[0]["Client Name"] == self.TEST_NAME

        # Clean up — delete the test row
        all_ids = [r.get("Booking ID") for r in rows]
        row_index = all_ids.index(booking_id) + 2  # +1 for header, +1 for 1-based index
        ws.delete_rows(row_index)

    def test_slot_available_on_far_future_date(self):
        # Date 2099-01-01 should always be free
        assert ss.is_slot_available(date(2099, 1, 1), time(9, 0), time(11, 0))
