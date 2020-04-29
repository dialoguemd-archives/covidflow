import logging
from random import randrange

from aiohttp import ClientSession

VALIDATION_CODE_LENGTH = 4

OUTPUT_CHANNEL_PARAM = "output_channel"
TWILIO_CHANNEL = "twilio"

NAME_KEY = "name"
SEND_VALIDATION_CODE_INTENT = "send_validation_code"

ENTITIES_KEY = "entities"
FIRST_NAME_ENTITY = "first_name"
VALIDATION_CODE_ENTITY = "validation_code"

HTTP_OK = 200

# This is the prefix of the internal Docker/Kubernetes network name of the Rasa core
# servers. It matches the service/component names defined in docker-compose.yml and
# app.yml.
CORE_SERVER_PREFIX = "core-"

logger = logging.getLogger(__name__)


def generate_validation_code() -> str:
    return str(randrange(10 ** VALIDATION_CODE_LENGTH)).zfill(VALIDATION_CODE_LENGTH)


async def send_validation_code(
    phone_number: str, language: str, first_name: str, validation_code: str
) -> bool:

    base_url = f"http://{CORE_SERVER_PREFIX}{language}:8080"
    url = f"{base_url}/conversations/{phone_number}/trigger_intent"
    params = {OUTPUT_CHANNEL_PARAM: TWILIO_CHANNEL}
    body = {
        NAME_KEY: SEND_VALIDATION_CODE_INTENT,
        ENTITIES_KEY: {
            FIRST_NAME_ENTITY: first_name,
            VALIDATION_CODE_ENTITY: validation_code,
        },
    }

    logger.info("Sending validation code: url=%s params=%s body=%s", url, params, body)

    async with ClientSession() as session:
        async with session.post(url, params=params, json=body) as response:
            if response.status != HTTP_OK:
                logger.error(
                    "Error occured while sending validation code: %s", response.text
                )

            return response.status == HTTP_OK
