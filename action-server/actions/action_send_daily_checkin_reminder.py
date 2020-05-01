import logging
import os
import urllib.parse
from typing import Any, Dict, List, Text

from hashids import Hashids
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from db.base import session_factory
from db.reminder import Reminder

from .lib.exceptions import InvalidExternalEventException, ReminderNotFoundException

logger = logging.getLogger(__name__)

METADATA_ENTITY_NAME = "metadata"
REMINDER_ID_PROPERTY_NAME = "reminder_id"

CHECKIN_BASE_URL_ENV_KEY = "DAILY_CHECKIN_BASE_URL"
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
        base_url = _get_env(CHECKIN_BASE_URL_ENV_KEY)

        # Always appending '/', `urljoin` will take care of removing superfluous slash.
        self.base_url = base_url + "/"
        self.hashids = Hashids(salt, min_length=min_length)

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

        if conversation_id != phone_number:
            raise InvalidExternalEventException(
                f"Phone number does not match sender_id: reminder_id={reminder_id} sender_id={conversation_id} phone_number={phone_number}"
            )

        checkin_url = urllib.parse.urljoin(self.base_url, hashed_id)

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
