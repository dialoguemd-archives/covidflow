from datetime import datetime
from unittest import TestCase

from covidflow.constants import FIRST_NAME_SLOT, METADATA_SLOT, PHONE_NUMBER_SLOT
from covidflow.db.reminder import Reminder, _uniformize_timezone

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

    def test_next_reminder_due_date(self):
        reminder = Reminder(
            created_at=datetime(
                year=2020, month=5, day=9, hour=15, minute=10, second=33
            ),
            last_reminded_at=None,
        )
        self.assertEqual(
            reminder.next_reminder_due_date,
            datetime(year=2020, month=5, day=10, hour=15, minute=10, second=33),
        )

        reminder = Reminder(
            created_at=datetime(
                year=2020, month=5, day=6, hour=11, minute=43, second=12
            ),
            last_reminded_at=datetime(
                year=2020, month=5, day=9, hour=15, minute=10, second=33
            ),
        )
        self.assertEqual(
            reminder.next_reminder_due_date,
            datetime(year=2020, month=5, day=10, hour=11, minute=43, second=12),
        )
