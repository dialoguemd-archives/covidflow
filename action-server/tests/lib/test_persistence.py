from typing import Any, Dict
from unittest import TestCase
from unittest.mock import call, patch

from covidflow.db.assessment import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    SYMPTOMS_SLOT,
    Assessment,
)
from covidflow.db.reminder import PHONE_NUMBER_SLOT, Reminder
from covidflow.lib.persistence import (
    METADATA_SLOT,
    REMINDER_ID_METADATA_PROPERTY,
    cancel_reminder,
    save_reminder,
    store_assessment,
)

HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4
ENV = {
    "REMINDER_ID_HASHIDS_SALT": HASHIDS_SALT,
    "REMINDER_ID_HASHIDS_MIN_LENGTH": str(HASHIDS_MIN_LENGTH),
}

REMINDER_ID = 1
HASHED_ID = "ZaeZ"

DEFAULT_ASSESSMENT_SLOT_VALUES: Dict[str, Any] = {
    SYMPTOMS_SLOT: "moderate",
    FEEL_WORSE_SLOT: True,
    HAS_COUGH_SLOT: True,
    HAS_DIFF_BREATHING_SLOT: True,
    HAS_FEVER_SLOT: True,
}

DEFAULT_SLOTS_VALUES: Dict[str, Any] = {
    METADATA_SLOT: {REMINDER_ID_METADATA_PROPERTY: HASHED_ID},
    **DEFAULT_ASSESSMENT_SLOT_VALUES,
    "ignored_solt": "Boba Fett",
}

DEFAULT_ASSESSMENT = Assessment(REMINDER_ID, attributes=DEFAULT_ASSESSMENT_SLOT_VALUES)


class PersistenceTest(TestCase):
    #####
    ## save_reminder

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    @patch.object(Reminder, "create_from_slot_values")
    @patch.object(Assessment, "create_from_slot_values")
    def test_save_reminder(
        self,
        create_assessment_from_slot_values,
        create_reminder_from_slot_values,
        mock_session_factory,
    ):
        REMINDER_ID = 42
        PHONE_NUMBER = "12223334444"
        SLOTS = {
            PHONE_NUMBER_SLOT: PHONE_NUMBER,
        }

        mock_session = mock_session_factory.return_value
        expected_assessment = create_assessment_from_slot_values.return_value
        expected_reminder = create_reminder_from_slot_values.return_value
        expected_reminder.id = REMINDER_ID
        expected_reminder.phone_number = PHONE_NUMBER

        # Save with success
        save_reminder(SLOTS)

        create_assessment_from_slot_values.assert_called_with(REMINDER_ID, SLOTS)
        mock_session.add.assert_has_calls(
            [call(expected_reminder), call(expected_assessment)]
        )
        mock_session.commit.assert_called()
        mock_session.rollback.assert_not_called()
        mock_session.close.assert_called()

        ## Save with failure
        mock_session.commit.side_effect = Exception("not this time")
        save_reminder(SLOTS)

        mock_session.add.assert_called()
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    #####
    ## cancel_reminder

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    def test_cancel_reminder_valid(self, mock_session_factory):
        mock_reminder = (
            mock_session_factory.return_value.query.return_value.get.return_value
        )

        cancel_reminder(DEFAULT_SLOTS_VALUES)
        self.assertIs(mock_reminder.is_canceled, True)

        mock_session_factory.return_value.commit.assert_called()
        mock_session_factory.return_value.close.assert_called()

    def test_cancel_reminder_missing_env(self):
        with self.assertRaises(Exception):
            cancel_reminder(DEFAULT_SLOTS_VALUES)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    def test_cancel_reminder_missing_reminder_id(self, mock_session_factory):
        with self.assertRaises(KeyError):
            cancel_reminder(DEFAULT_ASSESSMENT_SLOT_VALUES)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    def test_cancel_reminder_commit_error(self, mock_session_factory):
        mock_session_factory.return_value.commit.side_effect = Exception("no way")

        cancel_reminder(DEFAULT_SLOTS_VALUES)

        mock_session_factory.return_value.commit.assert_called()
        mock_session_factory.return_value.rollback.assert_called()
        mock_session_factory.return_value.close.assert_called()

    #####
    ## store_assessment

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    def test_store_assessment_valid(self, mock_session_factory):
        store_assessment(DEFAULT_SLOTS_VALUES)

        mock_session_factory.return_value.add.assert_called_with(DEFAULT_ASSESSMENT)
        mock_session_factory.return_value.commit.assert_called()
        mock_session_factory.return_value.close.assert_called()

    def test_store_assessment_missing_env(self):
        with self.assertRaises(Exception):
            store_assessment(DEFAULT_SLOTS_VALUES)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    def test_store_assessment_missing_reminder_id(self, mock_session_factory):
        with self.assertRaises(KeyError):
            store_assessment(DEFAULT_ASSESSMENT_SLOT_VALUES)

    @patch.dict("os.environ", ENV)
    @patch("covidflow.lib.persistence.session_factory")
    def test_store_assessment_commit_error_no_raise(self, mock_session_factory):
        mock_session_factory.return_value.commit.side_effect = Exception("no way")

        store_assessment(DEFAULT_SLOTS_VALUES)

        mock_session_factory.return_value.add.assert_called_with(DEFAULT_ASSESSMENT)
        mock_session_factory.return_value.commit.assert_called()
        mock_session_factory.return_value.rollback.assert_called()
        mock_session_factory.return_value.close.assert_called()
