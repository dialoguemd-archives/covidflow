import asyncio
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

from aiohttp import web

from covidflow.utils.phone_number_validation import (
    _generate_validation_code,
    send_validation_code,
)

from .fake_server import FakeServer

CORE_SERVER = "covidflow.utils.phone_number_validation.CORE_SERVER_PREFIX"


def create_api_success(data: dict = {}):
    return lambda: web.json_response(data)


def create_api_failure():
    return lambda: web.HTTPBadRequest()


def success_body_data(validation_code: str):
    return {
        "name": "send_validation_code",
        "entities": {"validation_code": validation_code, "first_name": "Myname"},
    }


class PhoneNumberValidationTest(TestCase):
    def _setUp(self, response: Callable[[], web.Response], number: str = ""):
        self.loop = asyncio.new_event_loop()
        self.server = FakeServer(
            f"/conversations/{number}/trigger_intent", response, port=8080
        )

        self.endpoint = patch(CORE_SERVER, "127.0.0.1")
        self.endpoint.start()

        self.loop.run_until_complete(self.server.start())

    def test_generate_validation_code(self):
        self._setUp(create_api_success(), "15145554321")

        async def run():
            validation_code = _generate_validation_code()
            self.assertEqual(len(validation_code), 4)
            self.assertTrue(validation_code.isnumeric())

        self.run = run

    @patch("covidflow.utils.phone_number_validation.ClientSession")
    def test_send_validation_code_555_number(self, mock_client_session):
        self._setUp(create_api_success(), "15145554321")

        async def run():
            validation_code = await send_validation_code("15145554321", "", "Myname")
            self.assertEqual(validation_code, "4321")
            mock_client_session.assert_not_called()

        self.run = run

    @patch("covidflow.utils.phone_number_validation.ClientSession")
    def test_send_validation_code_success(self, mock_client_session):
        self._setUp(create_api_success(success_body_data("1234")), "15148884321")

        async def run():
            validation_code = await send_validation_code("15148884321", "", "Myname")
            self.assertIsNotNone(validation_code)
            self.assertNotEqual(validation_code, "4321")

        self.run = run

    @patch("covidflow.utils.phone_number_validation.ClientSession")
    def test_send_validation_code_error(self, mock_client_session):
        self._setUp(create_api_failure(), "15148884321")

        async def run():
            validation_code = await send_validation_code("15148884321", "", "Myname")
            self.assertIsNone(validation_code)

        self.run = run

    def tearDown(self):
        self.loop.run_until_complete(self.run())
        self.loop.run_until_complete(self.server.stop())
        self.endpoint.stop()
