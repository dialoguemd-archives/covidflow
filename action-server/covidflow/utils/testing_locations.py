from copy import deepcopy
from typing import Iterable, Tuple, Union

import backoff
import structlog
from aiohttp import ClientError, ClientSession

logger = structlog.get_logger()

CLINIA_ENDPOINT = "https://covid.clinia.com"
CLINIA_API_ROUTE = "/api/v1/indexes/covid/query"

LOCATION_KEY = "aroundLatLng"
PAGE_KEY = "page"
HITS_KEY = "hits"

DEFAULT_SEARCH_PARAMETERS = {
    "perPage": 20,
    "rankingInfo": True,
    "facetFilters": [
        ["services.en:COVID-19 testing", "services.en:COVID-19 follow up testing",]
    ],
}


class TestingLocationAddress:
    def __init__(self, raw_address_data: dict):
        self.raw_address = raw_address_data

    @property
    def street_address(self) -> Union[None, str]:
        # ie: 5800 Cavendish Blvd
        return self.raw_address.get("streetAddress")

    @property
    def region_code(self) -> Union[None, str]:
        # ie: QC
        return self.raw_address.get("regionCode")

    @property
    def country(self) -> Union[None, str]:
        # ie: Canada
        return self.raw_address.get("country")

    @property
    def place(self) -> Union[None, str]:
        # ie: Lachine
        return self.raw_address.get("place")


class TestingLocationPhone:
    def __init__(self, raw_phone_data: dict):
        self.raw_phone = raw_phone_data

    @property
    def number(self) -> Union[None, str]:
        return self.raw_phone.get("number")

    @property
    def extension(self) -> Union[None, str]:
        return self.raw_phone.get("extension")


class TestingLocation:
    def __init__(self, raw_data: dict):
        self.raw_data = deepcopy(raw_data)

        raw_address_data = raw_data.get("address")
        self.address = (
            None
            if raw_address_data is None
            else TestingLocationAddress(raw_address_data)
        )

        raw_phones_data = raw_data.get("phones", [])
        self.phones = [TestingLocationPhone(i) for i in raw_phones_data]

    @property
    def name(self) -> Union[None, str]:
        return self.raw_data.get("name")

    @property
    def require_referal(self) -> Union[None, bool]:
        return self.raw_data.get("requireReferral")

    @property
    def require_appointment(self) -> Union[None, bool]:
        return self.raw_data.get("requireAppointment")

    @property
    def coordinates(self) -> Union[None, Tuple[float, float]]:
        geo_point = self.raw_data.get("_geoPoint")
        if geo_point is None:
            return None
        return (float(geo_point.get("lat")), float(geo_point.get("lon")))

    @property
    def clientele(self) -> Union[None, str]:
        return self.raw_data.get("clientele")

    @property
    def websites(self) -> Union[Iterable[str]]:
        return self.raw_data.get("websites", [])

    def __repr__(self):
        return repr(self.raw_data)


async def _fetch_testing_locations(
    session: ClientSession, latitude: float, longitude: float, page: int = 0
):
    body = {
        **DEFAULT_SEARCH_PARAMETERS,
        LOCATION_KEY: f"{latitude},{longitude}",
        PAGE_KEY: page,
    }

    url = f"{CLINIA_ENDPOINT}{CLINIA_API_ROUTE}"
    logger.debug(f"Fetching test sites", url=url, body=body)

    result = await session.post(url, json=body)
    return await result.json()


@backoff.on_exception(backoff.expo, ClientError, max_time=3)
async def _fetch_testing_locations_with_backoff(
    session: ClientSession, latitude: float, longitude: float, page: int = 0
):
    return await _fetch_testing_locations(
        session=session, latitude=latitude, longitude=longitude, page=page
    )


async def get_testing_locations(
    latitude: float, longitude: float
) -> Iterable[TestingLocation]:
    async with ClientSession(raise_for_status=True) as session:
        result = await _fetch_testing_locations_with_backoff(
            session=session, latitude=latitude, longitude=longitude
        )

        if result is None or HITS_KEY not in result:
            logger.debug(
                f"No testing location found for coordinates {latitude},{longitude}"
            )
            return []

        hits = result[HITS_KEY]
        logger.debug(
            f"Found {len(hits)} testing location for coordinates {latitude},{longitude}"
        )
        return [TestingLocation(i) for i in hits]
