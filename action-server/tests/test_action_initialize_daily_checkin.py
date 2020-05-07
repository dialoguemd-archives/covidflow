from collections import namedtuple
from unittest.mock import patch

from hashids import Hashids
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet

from actions.action_initialize_daily_checkin import ActionInitializeDailyCheckin
from actions.constants import (
    AGE_OVER_65_SLOT,
    FIRST_NAME_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIALOGUE_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    PRECONDITIONS_SLOT,
    PROVINCE_SLOT,
    SYMPTOMS_SLOT,
)
from tests.action_helper import ActionTestCase

HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4
hashids = Hashids(HASHIDS_SALT, min_length=HASHIDS_MIN_LENGTH)

NON_DEFAULT_REMINDER_VALUES = {
    FIRST_NAME_SLOT: "Robin",
    PROVINCE_SLOT: "nu",
    AGE_OVER_65_SLOT: True,
    PRECONDITIONS_SLOT: True,
    HAS_DIALOGUE_SLOT: True,
}

NON_DEFAULT_ASSESSMENT_VALUES = {
    LAST_SYMPTOMS_SLOT: "none",
    LAST_HAS_COUGH_SLOT: False,
    LAST_HAS_FEVER_SLOT: False,
    LAST_HAS_DIFF_BREATHING_SLOT: False,
}

NON_DEFAULT_ASSESSMENT_VALUES_ENTRY = {
    SYMPTOMS_SLOT: "none",
    HAS_COUGH_SLOT: False,
    HAS_DIFF_BREATHING_SLOT: False,
    HAS_FEVER_SLOT: False,
}

DEFAULT_VALUES = {
    FIRST_NAME_SLOT: None,
    PROVINCE_SLOT: None,
    AGE_OVER_65_SLOT: False,
    PRECONDITIONS_SLOT: False,
    HAS_DIALOGUE_SLOT: False,
    LAST_SYMPTOMS_SLOT: "moderate",
    LAST_HAS_COUGH_SLOT: False,
    LAST_HAS_FEVER_SLOT: False,
    LAST_HAS_DIFF_BREATHING_SLOT: False,
}

DEFAULT_REMINDER_ID = 1
DEFAULT_REMINDER_ID_HASH = hashids.encode(1)

ENV = {
    "REMINDER_ID_HASHIDS_SALT": HASHIDS_SALT,
    "REMINDER_ID_HASHIDS_MIN_LENGTH": str(HASHIDS_MIN_LENGTH),
}


def _create_tracker(reminder_id=DEFAULT_REMINDER_ID_HASH) -> Tracker:
    return Tracker(
        "sender_id",
        {"metadata": {"reminder_id": reminder_id}},
        {},
        [],
        False,
        None,
        {},
        "action_listen",
    )


class TestActionInitializeDailyCheckin(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None

        self.patcher = patch.dict("os.environ", ENV)
        self.patcher.start()
        self.action = ActionInitializeDailyCheckin()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def test_action_name(self):
        self.assertEqual(
            ActionInitializeDailyCheckin().name(), "action_initialize_daily_checkin",
        )

    @patch("actions.action_initialize_daily_checkin.session_factory")
    def test_happy_path(self, mock_session_factory):
        mock_session_factory.return_value.query.return_value.get.return_value = namedtuple(
            "Reminder", NON_DEFAULT_REMINDER_VALUES.keys()
        )(
            *NON_DEFAULT_REMINDER_VALUES.values()
        )
        mock_session_factory.return_value.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = namedtuple(
            "Assessment", NON_DEFAULT_ASSESSMENT_VALUES_ENTRY.keys()
        )(
            *NON_DEFAULT_ASSESSMENT_VALUES_ENTRY.values()
        )

        tracker = _create_tracker()

        self.run_action(tracker)

        self.assert_templates([])

        expected_slots = {
            **NON_DEFAULT_REMINDER_VALUES,
            **NON_DEFAULT_ASSESSMENT_VALUES,
        }

        self.assert_events(
            [SlotSet(slot, value) for slot, value in expected_slots.items()]
        )

        mock_session_factory.return_value.close.assert_called()

    @patch("actions.action_initialize_daily_checkin.session_factory")
    def test_reminder_not_found_default_user_values(self, mock_session_factory):
        mock_session_factory.return_value.query.return_value.get.return_value = None
        mock_session_factory.return_value.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = (
            None
        )

        tracker = _create_tracker()

        self.run_action(tracker)

        self.assert_templates([])

        expected_slots = DEFAULT_VALUES

        self.assert_events(
            [SlotSet(slot, value) for slot, value in expected_slots.items()]
        )

        mock_session_factory.return_value.close.assert_called()
