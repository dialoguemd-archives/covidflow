from typing import Iterable

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
    "facetFilters": ["services.en:COVID-19 screening"],
}

HTTP_OK = 200


async def _fetch_screening_locations(
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
async def _fetch_screening_locations_with_backoff(
    session: ClientSession, latitude: float, longitude: float, page: int = 0
):
    return await _fetch_screening_locations(
        session=session, latitude=latitude, longitude=longitude, page=page
    )


async def get_screening_locations(latitude: float, longitude: float) -> Iterable[dict]:
    async with ClientSession(raise_for_status=True) as session:
        result = await _fetch_screening_locations_with_backoff(
            session=session, latitude=latitude, longitude=longitude
        )

        if result is None or HITS_KEY not in result:
            logger.debug(
                f"No screening location found for coordinates {latitude},{longitude}"
            )
            return []

        hits = result[HITS_KEY]
        logger.debug(
            f"Found {len(hits)} screening location for coordinates {latitude},{longitude}"
        )
        return hits
