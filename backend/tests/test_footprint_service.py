"""
Tests for services/footprint_service.py

Unit tests mock out httpx so no real network calls are made.
The integration test hits live APIs and is skipped by default.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.footprint_service import get_building_perimeter_ft


# ── Helpers ────────────────────────────────────────────────────────────────────

def _nominatim_response(lat="42.123", lon="-83.456"):
    resp = MagicMock(spec=httpx.Response)
    resp.raise_for_status = MagicMock()
    resp.json.return_value = [{"lat": lat, "lon": lon}]
    return resp


def _overpass_response(nodes):
    resp = MagicMock(spec=httpx.Response)
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"elements": [{"geometry": nodes}]}
    return resp


def _overpass_empty():
    resp = MagicMock(spec=httpx.Response)
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"elements": []}
    return resp


# ── Unit tests ─────────────────────────────────────────────────────────────────

class TestGetBuildingPerimeterFt:

    @pytest.mark.asyncio
    async def test_returns_positive_perimeter(self):
        nodes = [
            {"lat": 42.0000, "lon": -83.0000},
            {"lat": 42.0001, "lon": -83.0000},
            {"lat": 42.0001, "lon": -83.0001},
            {"lat": 42.0000, "lon": -83.0001},
            {"lat": 42.0000, "lon": -83.0000},  # closed ring
        ]
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = _nominatim_response()
            mock_client.post.return_value = _overpass_response(nodes)

            result = await get_building_perimeter_ft("123 Maple Ave, Springfield, IL 62701")

        assert result > 0

    @pytest.mark.asyncio
    async def test_raises_on_empty_geocode(self):
        geo_resp = MagicMock(spec=httpx.Response)
        geo_resp.raise_for_status = MagicMock()
        geo_resp.json.return_value = []

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = geo_resp

            with pytest.raises(ValueError, match="Could not geocode"):
                await get_building_perimeter_ft("999 Fake St, Nowhere, XX 00000")

    @pytest.mark.asyncio
    async def test_raises_on_no_building_footprint(self):
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = _nominatim_response()
            mock_client.post.return_value = _overpass_empty()

            with pytest.raises(ValueError, match="No building footprint"):
                await get_building_perimeter_ft("123 Maple Ave, Springfield, IL 62701")

    @pytest.mark.asyncio
    async def test_raises_on_geocode_timeout_not_500(self):
        """Geocoding timeout must surface as ValueError (→ 422), not propagate as 500."""
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.ReadTimeout("timed out", request=None)

            with pytest.raises(ValueError, match="Geocoding timed out"):
                await get_building_perimeter_ft("123 Maple Ave, Springfield, IL 62701")

    @pytest.mark.asyncio
    async def test_raises_on_geocode_406_not_500(self):
        """HTTP 406 from Nominatim (bad User-Agent) must surface as ValueError, not 500."""
        mock_request = MagicMock()
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 406

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "406 Not Acceptable",
                request=mock_request,
                response=mock_response,
            )

            with pytest.raises(ValueError, match="406"):
                await get_building_perimeter_ft("310 Pasco DR NE, Renton, WA 98059")

    @pytest.mark.asyncio
    async def test_raises_on_overpass_error_not_500(self):
        """HTTP error from Overpass must be labelled as Overpass error, not geocoding."""
        mock_request = MagicMock()
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429

        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = _nominatim_response()
            mock_client.post.side_effect = httpx.HTTPStatusError(
                "429 Too Many Requests",
                request=mock_request,
                response=mock_response,
            )

            with pytest.raises(ValueError, match="Overpass"):
                await get_building_perimeter_ft("123 Maple Ave, Springfield, IL 62701")

    @pytest.mark.asyncio
    async def test_raises_on_connection_error_not_500(self):
        """Network errors must surface as ValueError (→ 422), not 500."""
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = httpx.ConnectError("connection refused")

            with pytest.raises(ValueError, match="Network error"):
                await get_building_perimeter_ft("123 Maple Ave, Springfield, IL 62701")

    @pytest.mark.asyncio
    async def test_raises_on_insufficient_geometry(self):
        with patch("httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_cls.return_value.__aenter__.return_value = mock_client
            mock_client.get.return_value = _nominatim_response()
            mock_client.post.return_value = _overpass_response([{"lat": 42.0, "lon": -83.0}])

            with pytest.raises(ValueError, match="insufficient geometry"):
                await get_building_perimeter_ft("123 Maple Ave, Springfield, IL 62701")


# ── Integration test (skipped unless RUN_FOOTPRINT_INTEGRATION=1) ──────────────

@pytest.mark.skipif(
    not os.getenv("RUN_FOOTPRINT_INTEGRATION"),
    reason="set RUN_FOOTPRINT_INTEGRATION=1 to run live API tests",
)
class TestFootprintIntegration:
    @pytest.mark.asyncio
    async def test_known_address_returns_perimeter(self):
        perimeter = await get_building_perimeter_ft(
            "1600 Pennsylvania Ave NW, Washington, DC 20500"
        )
        assert perimeter > 100, f"Expected a large building perimeter, got {perimeter:.1f} ft"
