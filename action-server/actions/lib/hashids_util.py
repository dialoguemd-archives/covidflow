import os

from hashids import Hashids

HASHIDS_SALT_ENV_KEY = "REMINDER_ID_HASHIDS_SALT"
HASHIDS_MIN_LENGTH_ENV_KEY = "REMINDER_ID_HASHIDS_MIN_LENGTH"


def create_hashids():
    salt = os.environ[HASHIDS_SALT_ENV_KEY]
    min_length = os.environ[HASHIDS_MIN_LENGTH_ENV_KEY]
    return Hashids(salt, min_length=min_length)


def encode_reminder_id(reminder_id: int) -> str:
    return create_hashids().encode(reminder_id)


def decode_reminder_id(reminder_id: int) -> int:
    return create_hashids().decode(reminder_id)[0]
