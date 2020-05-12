from typing import Any, Dict
from unittest import TestCase
from unittest.mock import patch

from toolz import dissoc

from covidflow.db.assessment import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    SYMPTOMS_SLOT,
    Assessment,
)
from covidflow.db.reminder import PHONE_NUMBER_SLOT, Reminder
from covidflow.utils.persistence import (
    METADATA_SLOT,
    REMINDER_ID_METADATA_PROPERTY,
    cancel_reminder,
    ci_enroll,
    save_assessment,
)

REMINDER_ID = 11
ASSESSMENT_ID = 42
HASHED_ID = "foo"

DEFAULT_ASSESSMENT_SLOTS: Dict[str, Any] = {
    SYMPTOMS_SLOT: "moderate",
    FEEL_WORSE_SLOT: True,
    HAS_COUGH_SLOT: True,
    HAS_DIFF_BREATHING_SLOT: True,
    HAS_FEVER_SLOT: True,
}
DEFAULT_REMINDER_SLOTS: Dict[str, Any] = {PHONE_NUMBER_SLOT: "12223334444"}
DEFAULT_555_REMINDER_SLOTS: Dict[str, Any] = {PHONE_NUMBER_SLOT: "12225554444"}

DEFAULT_SELF_ASSESSMENT_SLOTS: Dict[str, Any] = {
    **DEFAULT_REMINDER_SLOTS,
    **DEFAULT_ASSESSMENT_SLOTS,
    "ignored_slot": "Jango Fett",
}
DEFAULT_DAILY_CI_SLOTS: Dict[str, Any] = {
    METADATA_SLOT: {REMINDER_ID_METADATA_PROPERTY: HASHED_ID},
    **DEFAULT_ASSESSMENT_SLOTS,
    "ignored_slot": "Boba Fett",
}

DEFAULT_REMINDER = Reminder(id=REMINDER_ID, attributes=DEFAULT_REMINDER_SLOTS)
DEFAULT_555_REMINDER = Reminder(id=REMINDER_ID, attributes=DEFAULT_555_REMINDER_SLOTS)
DEFAULT_ASSESSMENT = Assessment(
    id=ASSESSMENT_ID, reminder_id=REMINDER_ID, attributes=DEFAULT_ASSESSMENT_SLOTS
)


def _set_id(x):
    if isinstance(x, Reminder):
        x.id = REMINDER_ID
    elif isinstance(x, Assessment):
        x.id = ASSESSMENT_ID
    else:
        raise


class AssessmentPersistenceTest(TestCase):
    @patch("covidflow.utils.persistence.encode_reminder_id", return_value=HASHED_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_save_reminder(self, mock_session_factory, mock_encode_reminder_id):
        mock_session = mock_session_factory.return_value
        mock_session.add.side_effect = _set_id

        ci_enroll(DEFAULT_SELF_ASSESSMENT_SLOTS)

        mock_session.add.assert_called_with(DEFAULT_ASSESSMENT)

    @patch("covidflow.utils.persistence.encode_reminder_id", return_value=HASHED_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_save_reminder_with_555_phone_number_does_nothing(
        self, mock_session_factory, mock_encode_reminder_id
    ):
        mock_session = mock_session_factory.return_value
        mock_session.add.side_effect = _set_id

        ci_enroll(DEFAULT_555_REMINDER_SLOTS)

        mock_session.add.assert_not_called()

    @patch("covidflow.utils.persistence.decode_reminder_id", return_value=REMINDER_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_cancel_reminder(self, mock_session_factory, mock_decode_reminder_id):
        mock_session = mock_session_factory.return_value
        mock_session.query.return_value.get.return_value = DEFAULT_REMINDER

        cancel_reminder(DEFAULT_DAILY_CI_SLOTS)

        self.assertIs(DEFAULT_REMINDER.is_canceled, True)

    @patch("covidflow.utils.persistence.decode_reminder_id", return_value=REMINDER_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_cancel_reminder_with_555_phone_number_does_nothing(
        self, mock_session_factory, mock_decode_reminder_id
    ):
        mock_session = mock_session_factory.return_value
        mock_session.query.return_value.get.return_value = DEFAULT_REMINDER

        cancel_reminder(
            {**DEFAULT_SELF_ASSESSMENT_SLOTS, PHONE_NUMBER_SLOT: "12225554444"}
        )

        mock_session.add.assert_not_called()

    @patch("covidflow.utils.persistence.decode_reminder_id", return_value=REMINDER_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_cancel_reminder_missing_metadata(
        self, mock_session_factory, mock_decode_reminder_id
    ):
        mock_session = mock_session_factory.return_value
        mock_session.query.return_value.get.return_value = DEFAULT_REMINDER

        daily_ci_slots_without_metadata = dissoc(DEFAULT_DAILY_CI_SLOTS, METADATA_SLOT)

        with self.assertRaises(expected_exception=Exception):
            # None metadata
            cancel_reminder(daily_ci_slots_without_metadata)

        with self.assertRaises(expected_exception=Exception):
            # Empty metadata
            cancel_reminder({**daily_ci_slots_without_metadata, METADATA_SLOT: {}})

        mock_session.add.assert_not_called()

    @patch("covidflow.utils.persistence.decode_reminder_id", return_value=REMINDER_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_save_assessment(self, mock_session_factory, mock_decode_reminder_id):
        mock_session = mock_session_factory.return_value
        mock_session.add.side_effect = _set_id
        mock_session.query.return_value.get.return_value = DEFAULT_REMINDER

        save_assessment(DEFAULT_DAILY_CI_SLOTS)

        mock_session.add.assert_called_with(DEFAULT_ASSESSMENT)

    @patch("covidflow.utils.persistence.decode_reminder_id", return_value=REMINDER_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_save_assessment_with_555_phone_number_does_nothing(
        self, mock_session_factory, mock_decode_reminder_id
    ):
        mock_session = mock_session_factory.return_value
        mock_session.add.side_effect = _set_id
        mock_session.query.return_value.get.return_value = DEFAULT_555_REMINDER

        save_assessment(DEFAULT_DAILY_CI_SLOTS)

        mock_session.add.assert_not_called()

    @patch("covidflow.utils.persistence.decode_reminder_id", return_value=REMINDER_ID)
    @patch("covidflow.utils.persistence.session_factory")
    def test_save_assessment_missing_metadata(
        self, mock_session_factory, mock_decode_reminder_id
    ):
        mock_session = mock_session_factory.return_value
        mock_session.add.side_effect = _set_id
        mock_session.query.return_value.get.return_value = DEFAULT_REMINDER

        daily_ci_slots_without_metadata = dissoc(DEFAULT_DAILY_CI_SLOTS, METADATA_SLOT)

        with self.assertRaises(expected_exception=Exception):
            # None metadata
            save_assessment(daily_ci_slots_without_metadata)

        with self.assertRaises(expected_exception=Exception):
            # Empty metadata
            save_assessment({**daily_ci_slots_without_metadata, METADATA_SLOT: {}})

        mock_session.add.assert_not_called()
