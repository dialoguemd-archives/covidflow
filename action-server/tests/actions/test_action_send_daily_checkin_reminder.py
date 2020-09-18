from datetime import datetime
from unittest import TestCase

import pytest
from asynctest.mock import patch
from hashids import Hashids
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from covidflow.actions.action_send_daily_checkin_reminder import (
    ActionSendDailyCheckInReminder,
)
from covidflow.constants import ACTION_LISTEN_NAME
from covidflow.exceptions import (
    InvalidExternalEventException,
    ReminderNotFoundException,
)

CHECKIN_URL_PATTERN = "http://test.com/?lng={language}#chat/ci/{reminder_id}"
HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4
hashids = Hashids(HASHIDS_SALT, min_length=HASHIDS_MIN_LENGTH)

DEFAULT_NOW = datetime(2000, 1, 1, 1, 1, 1)
DEFAULT_PHONE_NUMBER = "91112223333"
DEFAULT_FIRST_NAME = "George"
DEFAULT_LANGUAGE = "fr"
DEFAULT_REMINDER_ID = 1
DEFAULT_REMINDER_ID_HASH = hashids.encode(1)

ENV = {
    "REMINDER_ID_HASHIDS_SALT": HASHIDS_SALT,
    "REMINDER_ID_HASHIDS_MIN_LENGTH": str(HASHIDS_MIN_LENGTH),
    "DAILY_CHECKIN_URL_PATTERN": CHECKIN_URL_PATTERN,
}

INVALID_PATTERN_ENV = {
    "REMINDER_ID_HASHIDS_SALT": HASHIDS_SALT,
    "REMINDER_ID_HASHIDS_MIN_LENGTH": str(HASHIDS_MIN_LENGTH),
    "DAILY_CHECKIN_URL_PATTERN": "http://test.com/?lng={language}#chat/ci/{rem}",
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
        ACTION_LISTEN_NAME,
    )


def _mock_reminder(mock_session_factory, phone_number):
    reminder_mock = (
        mock_session_factory.return_value.query.return_value.get.return_value
    )
    reminder_mock.first_name = DEFAULT_FIRST_NAME
    reminder_mock.phone_number = phone_number
    reminder_mock.language = DEFAULT_LANGUAGE
    return reminder_mock


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

    @patch.dict("os.environ", INVALID_PATTERN_ENV)
    def test_invalid_url_pattern(self):
        with self.assertRaises(expected_exception=KeyError):
            ActionSendDailyCheckInReminder()

    @pytest.mark.asyncio
    @patch("covidflow.actions.action_send_daily_checkin_reminder.session_factory")
    @patch("covidflow.actions.action_send_daily_checkin_reminder.datetime")
    async def test_happy_path(self, mock_datetime, mock_session_factory):
        reminder_mock = _mock_reminder(mock_session_factory, DEFAULT_PHONE_NUMBER)
        mock_datetime.utcnow.return_value = DEFAULT_NOW

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        with patch.dict("os.environ", ENV):
            await ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})

        self.assertEqual(len(dispatcher.messages), 1)
        message = dispatcher.messages[0]

        self.assertEqual(message["template"], "utter_checkin_reminder")
        self.assertEqual(message["first_name"], DEFAULT_FIRST_NAME)
        self.assertEqual(
            message["check_in_url"],
            CHECKIN_URL_PATTERN.format(
                language=DEFAULT_LANGUAGE, reminder_id=DEFAULT_REMINDER_ID_HASH
            ),
        )

        self.assertEqual(reminder_mock.last_reminded_at, DEFAULT_NOW)
        mock_session_factory.return_value.commit.assert_called()
        mock_session_factory.return_value.close.assert_called()

    @pytest.mark.asyncio
    @patch("covidflow.actions.action_send_daily_checkin_reminder.session_factory")
    @patch("covidflow.actions.action_send_daily_checkin_reminder.datetime")
    async def test_555_phone_number_no_reminder(
        self, mock_datetime, mock_session_factory
    ):
        _mock_reminder(mock_session_factory, "12345556789")
        mock_datetime.utcnow.return_value = DEFAULT_NOW

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        with patch.dict("os.environ", ENV):
            await ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})

        self.assertListEqual(dispatcher.messages, [])
        mock_session_factory.return_value.commit.assert_called()
        mock_session_factory.return_value.close.assert_called()

    @pytest.mark.asyncio
    @patch("covidflow.actions.action_send_daily_checkin_reminder.session_factory")
    async def test_reminder_not_found(self, mock_session_factory):
        mock_session_factory.return_value.query.return_value.get.return_value = None

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        with patch.dict("os.environ", ENV):
            with self.assertRaises(expected_exception=ReminderNotFoundException):
                await ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})

        mock_session_factory.return_value.rollback.assert_called()
        mock_session_factory.return_value.close.assert_called()

    @pytest.mark.asyncio
    @patch("covidflow.actions.action_send_daily_checkin_reminder.session_factory")
    async def test_phone_not_match(self, mock_session_factory):
        _mock_reminder(mock_session_factory, "99999999999")

        tracker = _create_tracker()
        dispatcher = CollectingDispatcher()

        with patch.dict("os.environ", ENV):
            with self.assertRaises(expected_exception=InvalidExternalEventException):
                await ActionSendDailyCheckInReminder().run(dispatcher, tracker, {})

        mock_session_factory.return_value.rollback.assert_called()
        mock_session_factory.return_value.close.assert_called()
