from collections import namedtuple

import pytest
from asynctest.mock import patch
from hashids import Hashids
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet

from covidflow.actions.action_initialize_daily_checkin import (
    ActionInitializeDailyCheckin,
    _fill_symptoms,
)
from covidflow.constants import (
    ACTION_LISTEN_NAME,
    AGE_OVER_65_SLOT,
    FIRST_NAME_SLOT,
    HAS_DIALOGUE_SLOT,
    INVALID_REMINDER_ID_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    METADATA_SLOT,
    PRECONDITIONS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
    Symptoms,
)
from covidflow.db.assessment import (
    HAS_COUGH_ATTRIBUTE,
    HAS_DIFF_BREATHING_ATTRIBUTE,
    HAS_FEVER_ATTRIBUTE,
    SYMPTOMS_ATTRIBUTE,
)
from covidflow.db.reminder import (
    AGE_OVER_65_ATTRIBUTE,
    FIRST_NAME_ATTRIBUTE,
    HAS_DIALOGUE_ATTRIBUTE,
    PRECONDITIONS_ATTRIBUTE,
    PROVINCE_ATTRIBUTE,
)

from .action_test_helper import ActionTestCase

HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4
hashids = Hashids(HASHIDS_SALT, min_length=HASHIDS_MIN_LENGTH)

NON_DEFAULT_PROVINCE = "nu"
NON_DEFAULT_PROVINCIAL_811 = "811 special"
DEFAULT_PROVINCIAL_811 = "811 default"

DOMAIN = {
    "responses": {
        f"provincial_811_{NON_DEFAULT_PROVINCE}": [
            {"text": NON_DEFAULT_PROVINCIAL_811}
        ],
        "provincial_811_default": [{"text": DEFAULT_PROVINCIAL_811}],
    }
}

NON_DEFAULT_REMINDER_ATTRIBUTES = {
    FIRST_NAME_ATTRIBUTE: "Robin",
    PROVINCE_ATTRIBUTE: NON_DEFAULT_PROVINCE,
    AGE_OVER_65_ATTRIBUTE: True,
    PRECONDITIONS_ATTRIBUTE: True,
    HAS_DIALOGUE_ATTRIBUTE: True,
}

NON_DEFAULT_REMINDER_SLOTS = {
    FIRST_NAME_SLOT: "Robin",
    PROVINCE_SLOT: NON_DEFAULT_PROVINCE,
    AGE_OVER_65_SLOT: True,
    PRECONDITIONS_SLOT: True,
    HAS_DIALOGUE_SLOT: True,
}

NON_DEFAULT_ASSESSMENT_ATTRIBUTES = {
    SYMPTOMS_ATTRIBUTE: Symptoms.MODERATE,
    HAS_COUGH_ATTRIBUTE: False,
    HAS_FEVER_ATTRIBUTE: False,
    HAS_DIFF_BREATHING_ATTRIBUTE: False,
}

NON_DEFAULT_ASSESSMENT_SLOTS = {
    LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
    LAST_HAS_COUGH_SLOT: False,
    LAST_HAS_FEVER_SLOT: False,
    LAST_HAS_DIFF_BREATHING_SLOT: False,
}

DEFAULT_ASSESSMENT_SLOTS = {
    LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
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
        {METADATA_SLOT: {"reminder_id": reminder_id}},
        {},
        [],
        False,
        None,
        {},
        ACTION_LISTEN_NAME,
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

    def test_fill_symptoms(self):
        self.assertEqual(_fill_symptoms(Symptoms.MILD), Symptoms.MILD)
        self.assertEqual(_fill_symptoms(Symptoms.NONE), Symptoms.MILD)
        self.assertEqual(_fill_symptoms(Symptoms.MODERATE), Symptoms.MODERATE)
        self.assertEqual(_fill_symptoms(Symptoms.SEVERE), Symptoms.MODERATE)
        self.assertEqual(_fill_symptoms(None), Symptoms.MODERATE)

    @pytest.mark.asyncio
    @patch("covidflow.actions.action_initialize_daily_checkin.get_reminder")
    @patch("covidflow.actions.action_initialize_daily_checkin.get_last_assessment")
    async def test_happy_path(self, mock_get_last_assessment, mock_get_reminder):
        mock_get_reminder.return_value = namedtuple(
            "Reminder", NON_DEFAULT_REMINDER_ATTRIBUTES.keys()
        )(*NON_DEFAULT_REMINDER_ATTRIBUTES.values())
        mock_get_last_assessment.return_value = namedtuple(
            "Assessment", NON_DEFAULT_ASSESSMENT_ATTRIBUTES.keys()
        )(*NON_DEFAULT_ASSESSMENT_ATTRIBUTES.values())

        tracker = _create_tracker()

        await self.run_action(tracker, DOMAIN)

        self.assert_templates([])

        expected_slots = {
            **NON_DEFAULT_REMINDER_SLOTS,
            PROVINCIAL_811_SLOT: NON_DEFAULT_PROVINCIAL_811,
            **NON_DEFAULT_ASSESSMENT_SLOTS,
        }

        self.assert_events(
            [SlotSet(slot, value) for slot, value in expected_slots.items()]
        )

    @pytest.mark.asyncio
    @patch(
        "covidflow.actions.action_initialize_daily_checkin.get_reminder",
        side_effect=Exception,
    )
    @patch("covidflow.actions.action_initialize_daily_checkin.get_last_assessment")
    async def test_reminder_not_found(
        self, mock_get_last_assessment, mock_get_reminder
    ):
        mock_get_last_assessment.return_value = namedtuple(
            "Assessment", NON_DEFAULT_ASSESSMENT_ATTRIBUTES.keys()
        )(*NON_DEFAULT_ASSESSMENT_ATTRIBUTES.values())

        tracker = _create_tracker()

        await self.run_action(tracker, DOMAIN)

        self.assert_templates(
            [
                "utter_daily_ci__invalid_id__invalid_link",
                "utter_daily_ci__invalid_id__try_again",
            ]
        )

        self.assert_events([SlotSet(INVALID_REMINDER_ID_SLOT, True)])

    @pytest.mark.asyncio
    @patch("covidflow.actions.action_initialize_daily_checkin.get_reminder")
    @patch(
        "covidflow.actions.action_initialize_daily_checkin.get_last_assessment",
        side_effect=Exception,
    )
    async def test_assessment_not_found_default_values(
        self, mock_get_last_assessment, mock_get_reminder
    ):
        mock_get_reminder.return_value = namedtuple(
            "Reminder", NON_DEFAULT_REMINDER_ATTRIBUTES.keys()
        )(*NON_DEFAULT_REMINDER_ATTRIBUTES.values())

        tracker = _create_tracker()

        await self.run_action(tracker, DOMAIN)

        self.assert_templates([])

        expected_slots = {
            **NON_DEFAULT_REMINDER_SLOTS,
            PROVINCIAL_811_SLOT: NON_DEFAULT_PROVINCIAL_811,
            **DEFAULT_ASSESSMENT_SLOTS,
        }

        self.assert_events(
            [SlotSet(slot, value) for slot, value in expected_slots.items()]
        )
