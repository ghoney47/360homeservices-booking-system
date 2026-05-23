import math
import httpx

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
_NOMINATIM_HEADERS = {"User-Agent": "booking-system-gutter-estimator/1.0"}
_OVERPASS_RADIUS_M = 50  # metres around geocoded point to search for a building


def _haversine_ft(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R_ft = 20902231.0  # mean Earth radius in feet
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R_ft * math.asin(math.sqrt(a))


async def get_building_perimeter_ft(address: str) -> float:
    """Return the perimeter of the building footprint at *address* in linear feet.

    Geocodes via Nominatim (OSM) then queries Overpass for the building polygon.
    Raises ValueError if the address can't be geocoded or no footprint is found.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            geo_resp = await client.get(
                _NOMINATIM_URL,
                params={"q": address, "format": "json", "limit": 1},
                headers=_NOMINATIM_HEADERS,
            )
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()
            if not geo_data:
                raise ValueError(f"Could not geocode address: {address!r}")

            lat = float(geo_data[0]["lat"])
            lon = float(geo_data[0]["lon"])

            query = (
                f'[out:json];way["building"]'
                f'(around:{_OVERPASS_RADIUS_M},{lat},{lon});out geom;'
            )
            ov_resp = await client.post(_OVERPASS_URL, data={"data": query})
            ov_resp.raise_for_status()
            elements = ov_resp.json().get("elements", [])
    except ValueError:
        raise
    except httpx.TimeoutException:
        raise ValueError(
            f"Request timed out while looking up building footprint for: {address!r}"
        )
    except httpx.HTTPStatusError as exc:
        raise ValueError(
            f"Geocoding service returned an error ({exc.response.status_code}) "
            f"for: {address!r}"
        )
    except httpx.RequestError as exc:
        raise ValueError(
            f"Network error while looking up building footprint for {address!r}: {exc}"
        )

    if not elements:
        raise ValueError(
            f"No building footprint found in OpenStreetMap for: {address!r}"
        )

    nodes = elements[0].get("geometry", [])
    if len(nodes) < 2:
        raise ValueError("Building footprint returned insufficient geometry data")

    # OSM closes the ring by repeating the first node at the end
    perimeter = 0.0
    for i in range(len(nodes) - 1):
        perimeter += _haversine_ft(
            nodes[i]["lat"], nodes[i]["lon"],
            nodes[i + 1]["lat"], nodes[i + 1]["lon"],
        )
    return perimeter
