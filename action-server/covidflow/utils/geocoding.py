import os
from typing import Optional, Tuple

import googlemaps
import structlog

logger = structlog.get_logger()

GOOGLE_API_KEY_ENV = "GOOGLE_GEOCODING_API_KEY"

GEOMETRY = "geometry"
LOCATION = "location"
LATITUDE = "lat"
LONGITUDE = "lng"


class Geocoding:
    def __init__(self):
        key = os.environ[GOOGLE_API_KEY_ENV]
        self.client = googlemaps.Client(key=key)

    def get(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            geocode_result = self.client.geocode(address)

            if (len(geocode_result)) == 0:
                return None

            location = geocode_result[0].get(GEOMETRY, {}).get(LOCATION, {})

            if LATITUDE not in location or LONGITUDE not in location:
                return None

            return (location[LATITUDE], location[LONGITUDE])

        except:
            logger.exception(f"Error occured geocoding address: '{address}'")
            return None
