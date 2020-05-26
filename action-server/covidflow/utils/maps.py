import base64
import hashlib
import hmac
import os
from urllib.parse import urlencode

from .geocoding import Coordinates

GOOGLE_API_KEY_ENV = "GOOGLE_MAPS_API_KEY"
GOOGLE_SIGN_SECRET_ENV = "GOOGLE_MAPS_URL_SIGN_SECRET"

MAPS_ENDPOINT = "https://maps.googleapis.com"
MAPS_API_PATH = "/maps/api/staticmap"


def get_map_url(coordinates: Coordinates, size: str = "220x150", zoom: int = 15):
    key = os.environ[GOOGLE_API_KEY_ENV]
    secret = os.environ[GOOGLE_SIGN_SECRET_ENV]
    parameters = {
        "markers": f"{coordinates[0]},{coordinates[1]}",
        "zoom": zoom,
        "key": key,
        "size": size,
    }

    url_path = f"{MAPS_API_PATH}?{urlencode(parameters)}"
    signature = _create_signature(url_path, secret)

    return f"{MAPS_ENDPOINT}{url_path}&signature={signature}"


# More info here: https://developers.google.com/maps/documentation/maps-static/get-api-key#sample-code-for-url-signing
def _create_signature(url_path: str, secret: str) -> str:
    decoded_key = base64.urlsafe_b64decode(secret)
    signature = hmac.new(decoded_key, str.encode(url_path), hashlib.sha1)
    encoded_signature = base64.urlsafe_b64encode(signature.digest())
    return encoded_signature.decode()
