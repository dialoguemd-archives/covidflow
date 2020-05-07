import asyncio
import os
from datetime import datetime, timedelta

import aiohttp
import backoff
from aiohttp import ClientSession
from hashids import Hashids
from sqlalchemy import and_, or_
from structlog import get_logger

from actions.action_send_daily_checkin_reminder import (
    METADATA_ENTITY_NAME,
    REMINDER_ID_PROPERTY_NAME,
)
from db.base import session_factory
from db.reminder import Reminder

log = get_logger(__name__)

HASHIDS_SALT_ENV_KEY = "REMINDER_ID_HASHIDS_SALT"
HASHIDS_MIN_LENGTH_ENV_KEY = "REMINDER_ID_HASHIDS_MIN_LENGTH"

NAME_KEY = "name"
ENTITIES_KEY = "entities"

INTENT_NAME = "send_daily_checkin_reminder"
DEFAULT_ENDPOINTS = {"en": "core-en:8080", "fr": "core-fr:8080"}
URL_PATTERN = "http://{endpoint}/conversations/{phone_number}/trigger_intent?output_channel=twilio"


def run(
    hashids_salt=None, hashids_min_length=None, core_endpoints=DEFAULT_ENDPOINTS,
):
    log.info("Starting reminders job")

    salt = hashids_salt or os.environ[HASHIDS_SALT_ENV_KEY]
    min_length = hashids_min_length or os.environ[HASHIDS_MIN_LENGTH_ENV_KEY]

    hashids = Hashids(salt, min_length=min_length)

    reminders = _query_due_reminders()

    loop = asyncio.get_event_loop()
    sent, errored = loop.run_until_complete(
        _send_reminders(reminders, hashids, core_endpoints)
    )

    log.info(f"Reminders sent", sent_reminders=sent, errored_reminders=errored)
    return sent, errored


def _query_due_reminders():
    session = session_factory()
    now = datetime.utcnow()

    log.debug("Fetching due reminders")

    one_day_after_creation_date = and_(
        Reminder.last_reminded_at == None,
        Reminder.created_at <= now - timedelta(days=1),
    )
    one_day_after_last_reminder = Reminder.last_reminded_at <= now - timedelta(days=1)

    try:
        reminders = (
            session.query(Reminder)
            .filter(
                and_(
                    Reminder.is_canceled == False,
                    or_(one_day_after_creation_date, one_day_after_last_reminder),
                )
            )
            .all()
        )

        log.debug(f"Due reminders: {reminders}")

        return reminders
    finally:
        session.close()


async def _send_reminders(reminders, hashids, endpoints):
    sent = []
    errored = []

    async with ClientSession(raise_for_status=True) as session:
        for reminder in reminders:
            log.debug(f"Sending reminder: {reminder}")

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
            except Exception as e:
                errored.append(reminder.id)
                log.warning(f"Failed to send {reminder} due to {e!r}")

    return sent, errored


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=3)
async def _send_reminder_with_backoff(session, url, json):
    await _send_reminder(session, url, json)


async def _send_reminder(session, url, json):
    await session.post(url, json=json)


if __name__ == "__main__":
    run()
