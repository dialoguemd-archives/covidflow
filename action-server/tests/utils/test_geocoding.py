from unittest import TestCase
from unittest.mock import patch

from geopy.point import Point

from covidflow.utils.geocoding import Geocoding

ENV = {"GOOGLE_GEOCODING_API_KEY": "123abc"}

ADDRESS = "1 Christmas road, North Pole"
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

        location = Geocoding().get_from_address(ADDRESS)
        self.assertIsNone(location)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.geocoding.googlemaps")
    def test_get_geolocation_missing_keys(self, mock_googlemaps):
        client = mock_googlemaps.Client.return_value

        client.geocode.return_value = [{}]
        location = Geocoding().get_from_address(ADDRESS)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {}}]
        location = Geocoding().get_from_address(ADDRESS)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {"location": {}}}]
        location = Geocoding().get_from_address(ADDRESS)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {"location": {"lng": 45}}}]
        location = Geocoding().get_from_address(ADDRESS)
        self.assertIsNone(location)

        client.geocode.return_value = [{"geometry": {"location": {"lat": 45}}}]
        location = Geocoding().get_from_address(ADDRESS)
        self.assertIsNone(location)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.geocoding.googlemaps")
    def test_get_geolocation_address(self, mock_googlemaps):
        client = mock_googlemaps.Client.return_value

        client.geocode.return_value = [
            {"geometry": {"location": {"lat": 45, "lng": -75}}}
        ]
        location = Geocoding().get_from_address(ADDRESS)
        self.assertEqual(location, Point(45.0, -75.0))
        client.geocode.assert_called_once_with(address=ADDRESS)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.utils.geocoding.googlemaps")
    def test_get_geolocation_postal_code(self, mock_googlemaps):
        client = mock_googlemaps.Client.return_value

        client.geocode.return_value = [
            {"geometry": {"location": {"lat": 45, "lng": -75}}}
        ]
        location = Geocoding().get_from_postal_code(postal_code=POSTAL_CODE)
        self.assertEqual(location, Point(45.0, -75.0))
        client.geocode.assert_called_once_with(
            components={"postal_code": "H0H0H0", "country": "CA"}
        )
