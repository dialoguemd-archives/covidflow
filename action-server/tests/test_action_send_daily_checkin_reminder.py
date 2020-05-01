from unittest import TestCase
from unittest.mock import patch

from hashids import Hashids
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.action_send_daily_checkin_reminder import ActionSendDailyCheckInReminder
from actions.lib.exceptions import (
    InvalidExternalEventException,
    ReminderNotFoundException,
)

CHECKIN_BASE_URL = "http://test.com/ci/"
HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4
hashids = Hashids(HASHIDS_SALT, min_length=HASHIDS_MIN_LENGTH)

DEFAULT_PHONE_NUMBER = "91112223333"
DEFAULT_FIRST_NAME = "George"
DEFAULT_REMINDER_ID = 1
DEFAULT_REMINDER_ID_HASH = hashids.encode(1)

ENV = {
    "REMINDER_ID_HASHIDS_SALT": HASHIDS_SALT,
    "REMINDER_ID_HASHIDS_MIN_LENGTH": str(HASHIDS_MIN_LENGTH),
    "DAILY_CHECKIN_BASE_URL": CHECKIN_BASE_URL,
}


def _create_tracker(
    sender_id=DEFAULT_PHONE_NUMBER, reminder_id=DEFAULT_REMINDER_ID_HASH
) -> Tracker:
    return Tracker(
        sender_id,
        {},
        {"entities": [{"entity": "metadata", "value": {"reminder_id": reminder_id}}]},
        [],
        False,
        None,
        {},
        "action_listen",
    )


def _mock_reminder(mock_session_factory, phone_number):
    reminder_mock = (
        mock_session_factory.return_value.query.return_value.get.return_value
    )
    reminder_mock.first_name = DEFAULT_FIRST_NAME
    reminder_mock.phone_number = phone_number


class TestActionSendDailyCheckinReminder(TestCase):
    @patch.dict("os.environ", ENV)
    def test_action_name(self):
        self.assertEqual(
            ActionSendDailyCheckInReminder().name(),
            "action_send_daily_checkin_reminder",
        )

    def test_missing_environment_variables(self):
        with self.assertRaises(expected_exception=Exception):
            ActionSendDailyCheckInReminder()

    @patch.dict("os.environ", ENV)
    @patch("actions.action_send_daily_checkin_reminder.session_factory")
    def test_happy_path(self, mock_session_factory):
        _mock_reminder(mock_session_factory, DEFAULT_PHONE_NUMBER)

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})

        self.assertEqual(len(dispatcher.messages), 1)
        message = dispatcher.messages[0]

        self.assertEqual(message["template"], "utter_checkin_reminder")
        self.assertEqual(message["first_name"], DEFAULT_FIRST_NAME)
        self.assertEqual(
            message["check_in_url"], CHECKIN_BASE_URL + DEFAULT_REMINDER_ID_HASH,
        )

    @patch.dict("os.environ", ENV)
    @patch("actions.action_send_daily_checkin_reminder.session_factory")
    def test_reminder_not_found(self, mock_session_factory):
        mock_session_factory.return_value.query.return_value.get.return_value = None

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        with self.assertRaises(expected_exception=ReminderNotFoundException):
            ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})

    @patch.dict("os.environ", ENV)
    @patch("actions.action_send_daily_checkin_reminder.session_factory")
    def test_phone_not_match(self, mock_session_factory):
        _mock_reminder(mock_session_factory, "99999999999")

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        with self.assertRaises(expected_exception=InvalidExternalEventException):
            ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})
