from hashids import Hashids

from actions.lib.environment import get_env

HASHIDS_SALT_ENV_KEY = "REMINDER_ID_HASHIDS_SALT"
HASHIDS_MIN_LENGTH_ENV_KEY = "REMINDER_ID_HASHIDS_MIN_LENGTH"


def create_hashids():
    salt = get_env(HASHIDS_SALT_ENV_KEY)
    min_length = get_env(HASHIDS_MIN_LENGTH_ENV_KEY)
    return Hashids(salt, min_length=min_length)


def encode_reminder_id(reminder_id: int) -> str:
    return create_hashids().encode(reminder_id)


def decode_reminder_id(reminder_id: int) -> int:
    return create_hashids().decode(reminder_id)[0]
