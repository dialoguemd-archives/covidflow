# type: ignore
from unittest.mock import patch

import pytest
from rasa_sdk.events import Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT
from rasa_sdk.interfaces import ActionExecutionRejection

from actions.daily_ci_enroll_form import (
    CODE_TRY_COUNTER_SLOT,
    DO_ENROLL_SLOT,
    FIRST_NAME_SLOT,
    FORM_NAME,
    HAS_DIALOGUE_SLOT,
    PHONE_NUMBER_SLOT,
    PHONE_TRY_COUNTER_SLOT,
    PRE_EXISTING_CONDITIONS_SLOT,
    VALIDATION_CODE_REFERENCE_SLOT,
    VALIDATION_CODE_SLOT,
    WANTS_CANCEL_SLOT,
    DailyCiEnrollForm,
    _save_reminder,
)
from db.reminder import Reminder
from tests.form_helper import FormTestCase

FIRST_NAME = "John"
PHONE_NUMBER = "15145554567"
VALIDATION_CODE = "4567"

INITIAL_SLOT_VALUES = {
    PHONE_TRY_COUNTER_SLOT: 0,
    CODE_TRY_COUNTER_SLOT: 0,
    WANTS_CANCEL_SLOT: False,
}


class TestDailyCiEnrollForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiEnrollForm()

    def test_validate_first_name(self):
        slot_mapping = self.form.slot_mappings()[FIRST_NAME_SLOT]
        self.assertEqual(slot_mapping, self.form.from_text())

        self._validate_first_name("john", "john")
        self._validate_first_name("John", "John")
        self._validate_first_name("john john", "john john")

        # At the moment, we can't extract the name
        self._validate_first_name("it's John!", "it's John!")

    def _validate_first_name(self, text: str, expected_name: str):
        slot_values = self.form.validate_first_name(text, self.dispatcher, None, None)

        self.assertEqual({FIRST_NAME_SLOT: expected_name}, slot_values)

    @pytest.mark.asyncio
    async def test_validate_phone_number(self):
        slot_mapping = self.form.slot_mappings()[PHONE_NUMBER_SLOT]
        self.assertEqual(slot_mapping[-1], self.form.from_text())

        await self._validate_phone_number("5145554567", "15145554567")
        await self._validate_phone_number("15145554567", "15145554567")
        await self._validate_phone_number("514-555-4567", "15145554567")
        await self._validate_phone_number("1 (514)-555-4567", "15145554567")
        await self._validate_phone_number("it's 514-555-4567!", "15145554567")
        await self._validate_phone_number("it's 1 514 555 4567", "15145554567")

        await self._validate_phone_number("145554567", None)

    async def _validate_phone_number(self, text: str, expected_phone_number: str):
        tracker = self.create_tracker(
            slots={VALIDATION_CODE_REFERENCE_SLOT: VALIDATION_CODE}
        )
        slot_values = await self.form.validate_phone_number(
            text, self.dispatcher, tracker, None
        )

        self.assertEqual(
            expected_phone_number, slot_values.get(PHONE_NUMBER_SLOT, None)
        )

    def test_validate_validation_code_empty(self):
        slot_mapping = self.form.slot_mappings()[VALIDATION_CODE_SLOT]
        self.assertEqual(slot_mapping, self.form.from_text())

        self._validate_validation_code("its 4567", "4567")
        self._validate_validation_code("4567", "4567")

        self._validate_validation_code("45678", None)
        self._validate_validation_code("514", None)

        self._validate_validation_code("4325", None)

    def _validate_validation_code(self, text: str, expected_validation_code: str):
        tracker = self.create_tracker(
            slots={VALIDATION_CODE_REFERENCE_SLOT: VALIDATION_CODE}
        )
        slot_values = self.form.validate_daily_ci_enroll__validation_code(
            text, self.dispatcher, tracker, None
        )

        self.assertEqual(
            expected_validation_code, slot_values.get(VALIDATION_CODE_SLOT, None)
        )

    @patch("actions.daily_ci_enroll_form.session_factory")
    def test_save_reminder(self, mock_session_factory):
        mock_session = mock_session_factory.return_value

        reminder = Reminder(None)
        reminder.phone_number = "12223334444"
        _save_reminder(reminder)
        mock_session.add.assert_called_with(reminder)
        mock_session.commit.assert_called()
        mock_session.rollback.assert_not_called()
        mock_session.close.assert_called()

        mock_session.commit.side_effect = Exception("not this time")
        _save_reminder(reminder)
        mock_session.add.assert_called_with(reminder)
        mock_session.commit.assert_called()
        mock_session.rollback.assert_called()
        mock_session.close.assert_called()

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(tracker)

        self.assert_events([Form(FORM_NAME), SlotSet(REQUESTED_SLOT, DO_ENROLL_SLOT)])

        self.assert_templates(
            [
                "utter_daily_ci_enroll__offer_checkin",
                "utter_daily_ci_enroll__explain_checkin_1",
                "utter_daily_ci_enroll__explain_checkin_2",
                "utter_ask_daily_ci_enroll__do_enroll",
            ]
        )

    def test_provide_do_enroll_checkin_affirm(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: DO_ENROLL_SLOT}, intent="affirm"
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(DO_ENROLL_SLOT, True), SlotSet(REQUESTED_SLOT, FIRST_NAME_SLOT),],
        )

        self.assert_templates(
            ["utter_daily_ci_enroll__start_enroll", "utter_ask_first_name",],
        )

    def test_provide_do_enroll_checkin_deny(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: DO_ENROLL_SLOT}, intent="deny"
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(DO_ENROLL_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_first_name(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: FIRST_NAME_SLOT, DO_ENROLL_SLOT: True},
            text=FIRST_NAME,
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(FIRST_NAME_SLOT, FIRST_NAME),
                SlotSet(REQUESTED_SLOT, PHONE_NUMBER_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__thanks_first_name",
                "utter_daily_ci_enroll__text_message_checkin",
                "utter_ask_phone_number",
            ],
        )

    def test_provide_invalid_first_name(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: FIRST_NAME_SLOT, DO_ENROLL_SLOT: True}, text=" "
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(FIRST_NAME_SLOT, None), SlotSet(REQUESTED_SLOT, FIRST_NAME_SLOT),],
        )

        self.assert_templates(["utter_ask_first_name"])

    def test_provide_phone_number(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PHONE_NUMBER_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
            },
            text=PHONE_NUMBER,
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, PHONE_NUMBER),
                SlotSet(VALIDATION_CODE_REFERENCE_SLOT, VALIDATION_CODE),
                SlotSet(REQUESTED_SLOT, VALIDATION_CODE_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__acknowledge",
                "utter_ask_daily_ci_enroll__validation_code",
            ]
        )

    def test_provide_first_invalid_phone_number(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PHONE_NUMBER_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
            },
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, None),
                SlotSet(PHONE_TRY_COUNTER_SLOT, 1),
                SlotSet(REQUESTED_SLOT, PHONE_NUMBER_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__invalid_phone_number",
                "utter_ask_phone_number_error",
            ]
        )

    def test_provide_second_invalid_phone_number(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PHONE_NUMBER_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_TRY_COUNTER_SLOT: 1,
            },
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, None),
                SlotSet(PHONE_TRY_COUNTER_SLOT, 2),
                SlotSet(REQUESTED_SLOT, PHONE_NUMBER_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__invalid_phone_number",
                "utter_ask_phone_number_error",
            ]
        )

    def test_provide_third_invalid_phone_number(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PHONE_NUMBER_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_TRY_COUNTER_SLOT: 2,
            },
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, None),
                SlotSet(DO_ENROLL_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(["utter_daily_ci_enroll__invalid_phone_no_checkin"])

    def test_provide_no_phone_number(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PHONE_NUMBER_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
            },
            intent="no_phone",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, None),
                SlotSet(DO_ENROLL_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__no_phone_no_checkin",
                "utter_daily_ci_enroll__continue",
            ]
        )

    def test_provide_phone_number_cancel(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PHONE_NUMBER_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
            },
            intent="cancel",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, None),
                SlotSet(WANTS_CANCEL_SLOT, None),
                SlotSet(REQUESTED_SLOT, WANTS_CANCEL_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_daily_ci_enroll__wants_cancel"])

    def test_provide_wants_cancel_affirm(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: WANTS_CANCEL_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                WANTS_CANCEL_SLOT: None,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(WANTS_CANCEL_SLOT, True),
                SlotSet(DO_ENROLL_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(["utter_daily_ci_enroll__no_problem_continue"])

    def test_provide_wants_cancel_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: WANTS_CANCEL_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                WANTS_CANCEL_SLOT: None,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(WANTS_CANCEL_SLOT, False),
                SlotSet(PHONE_TRY_COUNTER_SLOT, 1),
                SlotSet(REQUESTED_SLOT, PHONE_NUMBER_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_daily_ci_enroll__ok_continue", "utter_ask_phone_number_error"]
        )

    def test_provide_validation_code(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: VALIDATION_CODE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_REFERENCE_SLOT: VALIDATION_CODE,
            },
            text=VALIDATION_CODE,
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(VALIDATION_CODE_SLOT, VALIDATION_CODE),
                SlotSet(REQUESTED_SLOT, PRE_EXISTING_CONDITIONS_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_daily_ci_enroll__thanks", "utter_ask_preconditions"]
        )

    def test_provide_first_invalid_validation_code(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: VALIDATION_CODE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_REFERENCE_SLOT: VALIDATION_CODE,
            },
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(VALIDATION_CODE_SLOT, None),
                SlotSet(CODE_TRY_COUNTER_SLOT, 1),
                SlotSet(REQUESTED_SLOT, VALIDATION_CODE_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_daily_ci_enroll__validation_code_error"])

    def test_provide_second_invalid_validation_code(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: VALIDATION_CODE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_REFERENCE_SLOT: VALIDATION_CODE,
                CODE_TRY_COUNTER_SLOT: 1,
            },
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(VALIDATION_CODE_SLOT, None),
                SlotSet(CODE_TRY_COUNTER_SLOT, 2),
                SlotSet(REQUESTED_SLOT, VALIDATION_CODE_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_daily_ci_enroll__validation_code_error"])

    def test_provide_third_invalid_validation_code(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: VALIDATION_CODE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_REFERENCE_SLOT: VALIDATION_CODE,
                CODE_TRY_COUNTER_SLOT: 2,
            },
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(VALIDATION_CODE_SLOT, None),
                SlotSet(DO_ENROLL_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(["utter_daily_ci_enroll__invalid_phone_no_checkin"])

    def test_provide_preconditions_affirm(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PRE_EXISTING_CONDITIONS_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_DIALOGUE_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_has_dialogue"])

    def test_provide_preconditions_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PRE_EXISTING_CONDITIONS_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_DIALOGUE_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_has_dialogue"],)

    def test_provide_preconditions_dont_know(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
            },
            intent="dont_know",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PRE_EXISTING_CONDITIONS_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_DIALOGUE_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_daily_ci_enroll__note_preconditions", "utter_ask_has_dialogue",],
        )

    def test_provide_preconditions_explain(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
            },
            intent="help_preconditions",
        )

        with self.assertRaises(ActionExecutionRejection):
            self.run_form(tracker)

    def test_provide_has_dialogue_affirm(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIALOGUE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
                PRE_EXISTING_CONDITIONS_SLOT: True,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIALOGUE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__enroll_done_1",
                "utter_daily_ci_enroll__enroll_done_2",
                "utter_daily_ci_enroll__enroll_done_3",
            ]
        )

    def test_provide_has_dialogue_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIALOGUE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
                PRE_EXISTING_CONDITIONS_SLOT: True,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIALOGUE_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__enroll_done_1",
                "utter_daily_ci_enroll__enroll_done_2",
                "utter_daily_ci_enroll__enroll_done_3",
            ],
        )

    @patch("actions.daily_ci_enroll_form._save_reminder")
    def test_provide_has_dialogue_enrollment_failed(self, mock_save_reminder):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIALOGUE_SLOT,
                DO_ENROLL_SLOT: True,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
                VALIDATION_CODE_SLOT: VALIDATION_CODE,
                PRE_EXISTING_CONDITIONS_SLOT: True,
            },
            intent="affirm",
        )

        mock_save_reminder.return_value = False

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIALOGUE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_enroll__enroll_fail_1",
                "utter_daily_ci_enroll__enroll_fail_2",
                "utter_daily_ci_enroll__enroll_fail_3",
            ]
        )

        expected_reminder = Reminder(None)
        expected_reminder.preconditions = True
        expected_reminder.first_name = FIRST_NAME
        expected_reminder.phone_number = PHONE_NUMBER
        expected_reminder.has_dialogue = True

        mock_save_reminder.assert_called_with(expected_reminder)
