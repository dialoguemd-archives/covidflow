import asyncio
from typing import Any, Callable
from unittest import TestCase
from unittest.mock import patch

from aiohttp import ClientResponseError, web
from aiohttp.test_utils import unused_port

from covidflow.utils.testing_locations import CLINIA_API_ROUTE
from covidflow.utils.testing_locations import TestingLocation as Location
from covidflow.utils.testing_locations import (
    _fetch_testing_locations,
    get_testing_locations,
)

from .fake_server import FakeServer

ENPOINT_FQN = "covidflow.utils.testing_locations.CLINIA_ENDPOINT"
FETCH_WITH_BACKOFF_FQN = (
    "covidflow.utils.testing_locations._fetch_testing_locations_with_backoff"
)


def create_api_success(data: Any = {}):
    return lambda: web.json_response(data)


def create_api_failure():
    return lambda: web.HTTPBadRequest()


class TestGetTestingLocations(TestCase):
    def _setUp(
        self, response: Callable[[], web.Response], start_server=True,
    ):
        loop = asyncio.get_event_loop()
        self.server = FakeServer(CLINIA_API_ROUTE, response)

        endpoint = (
            loop.run_until_complete(self.server.start())
            if start_server
            else f"http://127.0.0.1:{unused_port()}"
        )

        self.enpointPatch = patch(ENPOINT_FQN, endpoint)
        self.backoffPatch = patch(FETCH_WITH_BACKOFF_FQN, _fetch_testing_locations)
        self.enpointPatch.start()
        self.backoffPatch.start()

    def tearDown(self):
        self.enpointPatch.stop()
        self.backoffPatch.stop()
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.server.stop())
        except AttributeError:
            pass

    def _get_testing_locations(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_testing_locations(45, -75))

    def test_empty_result(self):
        self._setUp(create_api_success())

        actual = self._get_testing_locations()
        self.assertEqual(actual, [])

    def test_multiple_result(self):
        expected = [
            {"id": "result-1", "name": "name-1"},
            {"id": "result-1", "name": "name-1"},
        ]
        self._setUp(create_api_success({"hits": expected}))

        actual = self._get_testing_locations()
        self.assertEqual([i.raw_data for i in actual], expected)

    def test_failure(self):
        self._setUp(create_api_failure())

        with self.assertRaises(expected_exception=ClientResponseError):
            self._get_testing_locations()


SAMPLE = {
    "id": "0e6eadfe3f81ad8d910cfe00e6d65925",
    "address": {
        "country": "Canada",
        "unit": None,
        "regionCode": "QC",
        "streetAddress": "5800 Cavendish Blvd",
        "countryCode": "CA",
        "postalCode": "H4W 2T5",
        "place": "Côte Saint-Luc",
        "region": None,
    },
    "requireReferral": False,
    "_geoPoint": {"lon": -73.6662946, "lat": 45.4758369},
    "description": {"en": "en description", "fr": "fr description",},
    "phones": [{"number": "5146444545", "extension": None, "type": "MAIN"}],
    "services": {"en": ["COVID-19 screening"], "fr": ["Dépistage COVID-19"]},
    "requireAppointment": True,
    "clientele": "All",
    "instruction": None,
    "name": "Quartier Cavendish in Côte Saint-Luc",
    "websites": [
        "https://www.ciussswestcentral.ca/health-alerts/coronavirus-covid-19/covid-19-drive-through-screening-clinic/"
    ],
    "openingHours": {
        "sunday": [{"start": "10:00:00", "end": "16:00:00"}],
        "saturday": [{"start": "10:00:00", "end": "16:00:00"}],
        "tuesday": [{"start": "10:00:00", "end": "16:00:00"}],
        "wednesday": [{"start": "10:00:00", "end": "16:00:00"}],
        "thursday": [{"start": "10:00:00", "end": "16:00:00"}],
        "friday": [{"start": "10:00:00", "end": "16:00:00"}],
        "monday": [{"start": "10:00:00", "end": "16:00:00"}],
    },
    "_highlight": {},
    "_ranking": {"score": 6.982521, "distance": 11031.42529248569},
}


class TestTestingLocationsClasses(TestCase):
    def test_parse_sample(self):
        location = Location(SAMPLE)

        self.assertEqual(location.name, SAMPLE["name"])
        self.assertEqual(location.require_referal, SAMPLE["requireReferral"])
        self.assertEqual(location.require_appointment, SAMPLE["requireAppointment"])
        self.assertEqual(location.coordinates[0], SAMPLE["_geoPoint"]["lat"])
        self.assertEqual(location.coordinates[1], SAMPLE["_geoPoint"]["lon"])
        self.assertEqual(location.clientele, SAMPLE["clientele"])
        self.assertEqual(location.websites, SAMPLE["websites"])

        address = SAMPLE["address"]
        self.assertEqual(location.address.country, address["country"])
        self.assertEqual(location.address.region_code, address["regionCode"])
        self.assertEqual(location.address.street_address, address["streetAddress"])
        self.assertEqual(location.address.place, address["place"])

        self.assertEqual(location.phones[0].number, SAMPLE["phones"][0]["number"])
        self.assertEqual(location.phones[0].extension, SAMPLE["phones"][0]["extension"])

    def test_parse_empty(self):
        location = Location({})

        self.assertEqual(location.name, None)
        self.assertEqual(location.require_referal, None)
        self.assertEqual(location.require_appointment, None)
        self.assertEqual(location.coordinates, None)
        self.assertEqual(location.clientele, None)
        self.assertEqual(location.websites, [])
        self.assertEqual(location.address, None)
        self.assertEqual(location.phones, [])
