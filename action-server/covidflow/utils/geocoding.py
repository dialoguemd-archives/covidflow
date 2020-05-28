import os
from typing import Any, Dict, NamedTuple, Optional

import googlemaps
import structlog

logger = structlog.get_logger()

DEFAULT_COUNTRY = "CA"

GOOGLE_API_KEY_ENV = "GOOGLE_GEOCODING_API_KEY"

GEOMETRY = "geometry"
LOCATION = "location"
LATITUDE = "lat"
LONGITUDE = "lng"


class Coordinates(NamedTuple):
    latitude: float
    longitude: float


class Geocoding:
    def __init__(self):
        key = os.environ[GOOGLE_API_KEY_ENV]
        self.client = googlemaps.Client(key=key)

    def get_from_address(self, address: str) -> Optional[Coordinates]:
        request = {"address": address}
        return self._get_geocode(request)

    def get_from_postal_code(self, postal_code: str) -> Optional[Coordinates]:
        request = {
            "components": {"postal_code": postal_code, "country": DEFAULT_COUNTRY}
        }
        return self._get_geocode(request)

    def _get_geocode(self, request: Dict[str, Any]) -> Optional[Coordinates]:
        geocode_result = self.client.geocode(**request)

        if (len(geocode_result)) == 0:
            return None

        location = geocode_result[0].get(GEOMETRY, {}).get(LOCATION, {})

        if LATITUDE not in location or LONGITUDE not in location:
            return None

        return Coordinates(location[LATITUDE], location[LONGITUDE])
