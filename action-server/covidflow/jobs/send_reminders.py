import asyncio
import os
from datetime import datetime

import aiohttp
import backoff
from aiohttp import ClientSession
from hashids import Hashids
from sqlalchemy import and_
from structlog import get_logger

from ..actions.action_send_daily_checkin_reminder import (
    METADATA_ENTITY_NAME,
    REMINDER_ID_PROPERTY_NAME,
)
from ..db.base import session_factory
from ..db.reminder import Reminder

logger = get_logger(__name__)

EN = "en"
FR = "fr"


HASHIDS_SALT_ENV_KEY = "REMINDER_ID_HASHIDS_SALT"
HASHIDS_MIN_LENGTH_ENV_KEY = "REMINDER_ID_HASHIDS_MIN_LENGTH"
CORE_ENDPOINTS = {
    EN: "REMINDER_JOB_CORE_ENDPOINT_EN",
    FR: "REMINDER_JOB_CORE_ENDPOINT_FR",
}

NAME_KEY = "name"
ENTITIES_KEY = "entities"

INTENT_NAME = "send_daily_checkin_reminder"
DEFAULT_ENDPOINTS = {
    EN: "http://core-en.covidflow:8080",
    FR: "http://core-fr.covidflow:8080",
}
URL_PATTERN = (
    "{endpoint}/conversations/{phone_number}/trigger_intent?output_channel=twilio"
)


def run(
    hashids_salt=None, hashids_min_length=None, core_endpoints=DEFAULT_ENDPOINTS,
):
    logger.info("Starting reminders job")

    salt = hashids_salt or os.environ[HASHIDS_SALT_ENV_KEY]
    min_length = hashids_min_length or os.environ[HASHIDS_MIN_LENGTH_ENV_KEY]

    try:
        endpoints = {k: os.environ[v] for k, v in CORE_ENDPOINTS.items()}
    except KeyError:
        endpoints = core_endpoints

    hashids = Hashids(salt, min_length=min_length)

    reminders = _query_due_reminders()

    loop = asyncio.get_event_loop()
    sent, errored = loop.run_until_complete(
        _send_reminders(reminders, hashids, endpoints)
    )

    logger.info("Sent reminders", sent_reminders=sent, errored_reminders=errored)
    return sent, errored


def _query_due_reminders():
    session = session_factory()
    now = datetime.utcnow()

    logger.debug("Fetching due reminders")

    try:
        reminders = (
            session.query(Reminder)
            .filter(
                and_(
                    Reminder.is_canceled == False,
                    Reminder.next_reminder_due_date <= now,
                )
            )
            .all()
        )

        logger.debug("Fetched due reminders", reminders=reminders)

        return reminders
    except Exception:
        logger.exception("Failed to fetch due reminers")
        return []
    finally:
        session.close()


async def _send_reminders(reminders, hashids, endpoints):
    sent = []
    errored = []

    async with ClientSession(raise_for_status=True) as session:
        for reminder in reminders:
            logger.debug("Sending reminder", reminder=reminder)

            hashed_id = hashids.encode(reminder.id)
            url = URL_PATTERN.format(
                endpoint=endpoints[reminder.language],
                phone_number=reminder.phone_number,
            )
            json = {
                NAME_KEY: INTENT_NAME,
                ENTITIES_KEY: {
                    METADATA_ENTITY_NAME: {REMINDER_ID_PROPERTY_NAME: hashed_id}
                },
            }

            try:
                await _send_reminder_with_backoff(session, url, json)
                sent.append(reminder.id)
                logger.debug("Sent reminder", reminder=reminder)
            except Exception:
                errored.append(reminder.id)
                logger.warning(
                    "Failed to send reminder", reminder=reminder, exc_info=True
                )

    return sent, errored


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=3)
async def _send_reminder_with_backoff(session, url, json):
    await _send_reminder(session, url, json)


async def _send_reminder(session, url, json):
    await session.post(url, json=json)


if __name__ == "__main__":
    run()
