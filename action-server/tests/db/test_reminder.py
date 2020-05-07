from unittest import TestCase

from db.reminder import Reminder, _uniformize_timezone

METADATA_SLOT = "metadata"
PHONE_NUMBER_SLOT = "phone_number"
FIRST_NAME_SLOT = "first_name"
TIMEZONE_PROPERTY = "timezone"

PHONE_NUMBER = "15141112222"
TIMEZONE = "America/Toronto"
NAME = "Bob"


class TestReminder(TestCase):
    def test_create_from_slot_values(self):
        reminder = Reminder.create_from_slot_values(
            {
                METADATA_SLOT: {TIMEZONE_PROPERTY: TIMEZONE},
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                FIRST_NAME_SLOT: NAME,
                "ignored_slot": "value",
            }
        )
        expected_reminder = Reminder(TIMEZONE)
        expected_reminder.phone_number = PHONE_NUMBER
        expected_reminder.first_name = NAME

        self.assertEqual(reminder, expected_reminder)

    def test_uniformize_timezone(self):
        self.assertEqual(_uniformize_timezone("america/toronto"), "America/Toronto")
        self.assertEqual(_uniformize_timezone("does-not-exist"), None)
        self.assertEqual(_uniformize_timezone(None), None)

    def test_metadata_none(self):
        reminder = Reminder.create_from_slot_values(
            {
                METADATA_SLOT: None,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                FIRST_NAME_SLOT: NAME,
            }
        )
        expected_reminder = Reminder(timezone=None)
        expected_reminder.phone_number = PHONE_NUMBER
        expected_reminder.first_name = NAME

        self.assertEqual(reminder, expected_reminder)
