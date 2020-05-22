from unittest import TestCase
from unittest.mock import patch

from covidflow.utils.geocoding import Geocoding

ENV = {"GOOGLE_GEOCODING_API_KEY": "123abc"}

POSTAL_CODE = "H0H0H0"


class GeocodingTest(TestCase):
    def test_missing_environment_key(self):
        with self.assertRaises(expected_exception=KeyError):
            Geocoding()

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.geocoding.googlemaps")
    def test_get_geolocation_empty(self, mock_googlemaps):
        client = mock_googlemaps.Client.return_value
        client.geocode.return_value = []

        location = Geocoding().get(POSTAL_CODE)
        self.assertIsNone(location)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.geocoding.googlemaps")
    def test_get_geolocation_missing_keys(self, mock_googlemaps):
        client = mock_googlemaps.Client.return_value

        client.geocode.return_value = [{}]
        location = Geocoding().get(POSTAL_CODE)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {}}]
        location = Geocoding().get(POSTAL_CODE)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {"location": {}}}]
        location = Geocoding().get(POSTAL_CODE)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {"location": {"lng": 45}}}]
        location = Geocoding().get(POSTAL_CODE)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {"location": {"lat": 45}}}]
        location = Geocoding().get(POSTAL_CODE)
        self.assertIsNone(location)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.geocoding.googlemaps")
    def test_get_geolocation(self, mock_googlemaps):
        client = mock_googlemaps.Client.return_value

        client.geocode.return_value = [
            {"geometry": {"location": {"lat": 45, "lng": -75}}}
        ]
        location = Geocoding().get(POSTAL_CODE)
        self.assertEqual(location, (45, -75))
