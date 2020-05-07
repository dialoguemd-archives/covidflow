from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

from actions.lib.assessment_persistence import (
    METADATA_SLOT,
    REMINDER_ID_METADATA_PROPERTY,
    store_assessment,
)
from db.assessment import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    SYMPTOMS_SLOT,
    Assessment,
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


class AssessmentPersistenceTest(TestCase):
    @patch.dict("os.environ", ENV)
    @patch("actions.lib.assessment_persistence.session_factory")
    def test_store_assessment_valid(self, mock_session_factory):
        store_assessment(DEFAULT_SLOTS_VALUES)

        mock_session_factory.return_value.add.assert_called_with(DEFAULT_ASSESSMENT)
        mock_session_factory.return_value.commit.assert_called
        mock_session_factory.return_value.close.assert_called

    def test_store_assessment_missing_env(self):
        with self.assertRaises(Exception):
            store_assessment(DEFAULT_SLOTS_VALUES)

    @patch.dict("os.environ", ENV)
    @patch("actions.lib.assessment_persistence.session_factory")
    def test_store_assessment_missing_reminder_id(self, mock_session_factory):
        with self.assertRaises(KeyError):
            store_assessment(DEFAULT_ASSESSMENT_SLOT_VALUES)

    @patch.dict("os.environ", ENV)
    @patch("actions.lib.assessment_persistence.session_factory")
    def test_store_assessment_commit_error_no_raise(self, mock_session_factory):
        mock_session_factory.return_value.commit.side_effects = Exception("no way")

        store_assessment(DEFAULT_SLOTS_VALUES)

        mock_session_factory.return_value.add.assert_called_with(DEFAULT_ASSESSMENT)
        mock_session_factory.return_value.commit.assert_called
        mock_session_factory.return_value.rollback.assert_called
        mock_session_factory.return_value.close.assert_called
