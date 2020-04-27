from rasa_sdk.events import Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT
from rasa_sdk.interfaces import ActionExecutionRejection

from actions.daily_ci_enroll_form import (
    FIRST_NAME_SLOT,
    FORM_NAME,
    PHONE_NUMBER_SLOT,
    PRE_EXISTING_CONDITIONS_SLOT,
    DailyCiEnrollForm,
)
from tests.form_helper import FormTestCase

FIRST_NAME = "John"
PHONE_NUMBER = "5141234567"


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

    def test_validate_phone_number(self):
        slot_mapping = self.form.slot_mappings()[PHONE_NUMBER_SLOT]
        self.assertEqual(slot_mapping, self.form.from_text())

        self._validate_phone_number("5141234567", "5141234567")
        self._validate_phone_number("514-123-4567", "5141234567")
        self._validate_phone_number("(514)-123-4567", "5141234567")
        self._validate_phone_number("it's 514-123-4567!", "5141234567")
        self._validate_phone_number("it's 514 123 4567", "5141234567")

        self._validate_phone_number("141234567", None)

    def _validate_phone_number(self, text: str, expected_phone_number: str):
        slot_values = self.form.validate_phone_number(text, self.dispatcher, None, None)

        self.assertEqual({PHONE_NUMBER_SLOT: expected_phone_number}, slot_values)

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(tracker)

        self.assert_events([Form(FORM_NAME), SlotSet(REQUESTED_SLOT, FIRST_NAME_SLOT)],)

        self.assert_templates(["utter_ask_first_name"])

    def test_provide_first_name(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: FIRST_NAME_SLOT}, text=FIRST_NAME
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
                "utter_thanks_first_name",
                "utter_text_message_checkin",
                "utter_ask_phone_number",
            ],
        )

    def test_provide_invalid_first_name(self):
        tracker = self.create_tracker(slots={REQUESTED_SLOT: FIRST_NAME_SLOT}, text=" ")

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(FIRST_NAME_SLOT, None), SlotSet(REQUESTED_SLOT, FIRST_NAME_SLOT),],
        )

        self.assert_templates(["utter_ask_first_name"])

    def test_provide_phone_number(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: PHONE_NUMBER_SLOT, FIRST_NAME_SLOT: FIRST_NAME},
            text=PHONE_NUMBER,
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, PHONE_NUMBER),
                SlotSet(REQUESTED_SLOT, PRE_EXISTING_CONDITIONS_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_acknowledge", "utter_ask_pre_existing_conditions"]
        )

    def test_provide_invalid_phone_number(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: PHONE_NUMBER_SLOT, FIRST_NAME_SLOT: FIRST_NAME},
            text=" ",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PHONE_NUMBER_SLOT, None),
                SlotSet(REQUESTED_SLOT, PHONE_NUMBER_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_phone_number"])

    def test_provide_pre_existing_conditions(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PRE_EXISTING_CONDITIONS_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_answers_recorded",
                "utter_daily_ci_enroll_done",
                "utter_daily_ci_enroll_follow_up",
            ]
        )

    def test_provide_pre_existing_conditions_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PRE_EXISTING_CONDITIONS_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci_answers_recorded",
                "utter_daily_ci_enroll_done",
                "utter_daily_ci_enroll_follow_up",
            ],
        )

    def test_provide_pre_existing_conditions_dont_know(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
            },
            intent="dont_know",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PRE_EXISTING_CONDITIONS_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_note_pre_existing_conditions",
                "utter_daily_ci_answers_recorded",
                "utter_daily_ci_enroll_done",
                "utter_daily_ci_enroll_follow_up",
            ],
        )

    def test_provide_pre_existing_conditions_explain(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PRE_EXISTING_CONDITIONS_SLOT,
                FIRST_NAME_SLOT: FIRST_NAME,
                PHONE_NUMBER_SLOT: PHONE_NUMBER,
            },
            intent="help_pre_existing_conditions",
        )

        with self.assertRaises(ActionExecutionRejection):
            self.run_form(tracker)
