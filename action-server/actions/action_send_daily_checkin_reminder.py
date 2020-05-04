import logging
import os
from typing import Any, Dict, List, Text

from hashids import Hashids
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.lib.exceptions import (
    InvalidExternalEventException,
    ReminderNotFoundException,
)
from db.base import session_factory
from db.reminder import Reminder

logger = logging.getLogger(__name__)

METADATA_ENTITY_NAME = "metadata"
REMINDER_ID_PROPERTY_NAME = "reminder_id"

CHECKIN_URL_PATTERN_ENV_KEY = "DAILY_CHECKIN_URL_PATTERN"
HASHIDS_SALT_ENV_KEY = "REMINDER_ID_HASHIDS_SALT"
HASHIDS_MIN_LENGTH_ENV_KEY = "REMINDER_ID_HASHIDS_MIN_LENGTH"


def _query_reminder(reminder_id):
    session = session_factory()
    try:
        reminder = session.query(Reminder).get(reminder_id)
        if reminder is None:
            raise ReminderNotFoundException(
                f"Reminder with id '{reminder_id}' does not exist."
            )
        return reminder
    finally:
        session.close()


def _get_env(name):
    value = os.environ.get(name)
    if value is None:
        raise Exception(f"Environment variable '{name}' is not set.")
    return value


class ActionSendDailyCheckInReminder(Action):
    def __init__(self):
        salt = _get_env(HASHIDS_SALT_ENV_KEY)
        min_length = _get_env(HASHIDS_MIN_LENGTH_ENV_KEY)

        self.url_pattern = _get_env(CHECKIN_URL_PATTERN_ENV_KEY)
        self.hashids = Hashids(salt, min_length=min_length)

        try:
            # Make sure url pattern contains all required keys
            self.url_pattern.format(reminder_id="1", language="fr")
        except KeyError as exception:
            raise KeyError(
                f"Invalid value for {CHECKIN_URL_PATTERN_ENV_KEY} environment variable ({self.url_pattern})"
            ) from exception

    def name(self) -> Text:
        return "action_send_daily_checkin_reminder"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        metadata = next(tracker.get_latest_entity_values(METADATA_ENTITY_NAME))
        hashed_id = metadata[REMINDER_ID_PROPERTY_NAME]
        reminder_id = self.hashids.decode(hashed_id)[0]

        conversation_id = tracker.sender_id

        reminder = _query_reminder(reminder_id)
        first_name = reminder.first_name
        phone_number = reminder.phone_number
        language = reminder.language

        if conversation_id != phone_number:
            raise InvalidExternalEventException(
                f"Phone number does not match sender_id: reminder_id={reminder_id} sender_id={conversation_id} phone_number={phone_number}"
            )

        checkin_url = self.url_pattern.format(reminder_id=hashed_id, language=language)

        logger.debug(
            "Sending daily check-in reminder: checkin_url=%s first_name=%s.",
            checkin_url,
            first_name,
        )

        dispatcher.utter_message(
            template="utter_checkin_reminder",
            first_name=first_name,
            check_in_url=checkin_url,
        )

        return []
