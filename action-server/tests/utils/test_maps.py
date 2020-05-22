from unittest import TestCase
from unittest.mock import patch

from covidflow.utils.maps import _create_signature, get_map_url

ENV = {"GOOGLE_MAPS_API_KEY": "123abc", "GOOGLE_MAPS_URL_SIGN_SECRET": "123"}

COORDINATES = (-82.109835, 74.625658)


class GeocodingTest(TestCase):
    def test_missing_environment_key(self):
        with self.assertRaises(expected_exception=KeyError):
            get_map_url(COORDINATES)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.maps._create_signature", return_value="bobafett")
    def test_get_map(self, mock_create_signature):
        self.assertEqual(
            get_map_url(COORDINATES),
            "https://maps.googleapis.com/maps/api/staticmap?markers=-82.109835%2C74.625658&zoom=15&key=123abc&size=220x150&signature=bobafett",
        )

    def test_create_signature(self):
        self.assertEqual(
            _create_signature("/fake?parameter=234", "FAKE_g_grtGtg09htKfligrtrjk="),
            "5FTiBvO-6hq8xUJmKwWMLv9Gx4A=",
        )
