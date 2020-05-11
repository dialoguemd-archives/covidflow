# type: ignore
from unittest import TestCase, skip
from unittest.mock import patch

import pytest

from covidflow.lib.phone_number_validation import (
    _generate_validation_code,
    send_validation_code,
)

# Async mocking problem:
# See https://bugs.python.org/issue36996. It was solved, but not in Python 3.6.8,
# thus some tests had to be skipped. Since we do not intend to change the python
# version, no issue was create to fix this.


class PhoneNumberValidationTest(TestCase):
    def test_generate_validation_code(self):
        validation_code = _generate_validation_code()
        self.assertEqual(len(validation_code), 4)
        self.assertTrue(validation_code.isnumeric())

    @pytest.mark.asyncio
    @patch("covidflow.lib.phone_number_validation.ClientSession")
    async def test_send_validation_code_555_number(self, mock_client_session):
        validation_code = await send_validation_code("15145554321", "fr", "Myname")
        self.assertEqual(validation_code, "4321")
        mock_client_session.assert_not_called()

    @skip("Async mocking problem")
    @pytest.mark.asyncio
    @patch("covidflow.lib.phone_number_validation.ClientSession")
    async def test_send_validation_code_success(self, mock_client_session):
        print(mock_client_session)
        mock_client_session.return_value.post.return_value = {"status": 200}
        validation_code = await send_validation_code("15148884321", "fr", "Myname")
        mock_client_session.return_value.post.assert_called_once_with(
            url="http://core-fr:8080/conversations/15148884321/trigger_intent",
            params={"output_channel": "twilio"},
            body={
                "name": "send_validation_code",
                "entities": {
                    "validation_code": validation_code,
                    "first_name": "Myname",
                },
            },
        )
        self.assertNotEqual(validation_code, "4321")

    @skip("Async mocking problem")
    @pytest.mark.asyncio
    @patch("covidflow.lib.phone_number_validation.ClientSession")
    async def test_send_validation_code_error(self, mock_client_session):
        mock_client_session.return_value.post.return_value = {"status": 500}
        validation_code = await send_validation_code("15148884321", "fr", "Myname")

        self.assertIsNone(validation_code)
