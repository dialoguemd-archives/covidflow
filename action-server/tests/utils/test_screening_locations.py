import asyncio
from typing import Any, Callable
from unittest import TestCase
from unittest.mock import patch

from aiohttp import ClientResponseError, web
from aiohttp.test_utils import unused_port

from covidflow.utils.screening_locations import (
    CLINIA_API_ROUTE,
    _fetch_screening_locations,
    get_screening_locations,
)

from .fake_server import FakeServer

ENPOINT_FQN = "covidflow.utils.screening_locations.CLINIA_ENDPOINT"
FETCH_WITH_BACKOFF_FQN = (
    "covidflow.utils.screening_locations._fetch_screening_locations_with_backoff"
)


def create_api_success(data: Any = {}):
    return lambda: web.json_response(data)


def create_api_failure():
    return lambda: web.HTTPBadRequest()


class TestScreeningLocations(TestCase):
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
        self.backoffPatch = patch(FETCH_WITH_BACKOFF_FQN, _fetch_screening_locations)
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

    def _get_screening_locations(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(get_screening_locations(45, -75))

    def test_empty_result(self):
        self._setUp(create_api_success())

        actual = self._get_screening_locations()
        self.assertEqual(actual, [])

    def test_multiple_result(self):
        expected = [
            {"id": "result-1", "name": "name-1"},
            {"id": "result-1", "name": "name-1"},
        ]
        self._setUp(create_api_success({"hits": expected}))

        actual = self._get_screening_locations()
        self.assertEqual(actual, expected)

    def test_failure(self):
        self._setUp(create_api_failure())

        with self.assertRaises(expected_exception=ClientResponseError):
            self._get_screening_locations()
