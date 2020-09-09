from rasa_sdk.events import SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.new_assessment_form.validate_new_assessment_form import (
    FORM_NAME,
    SKIP_SLOT_PLACEHOLDER,
    ValidateNewAssessmentForm,
)
from covidflow.constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)
from tests.actions.validate_action_test_helper import ValidateActionTestCase

DOMAIN = {"responses": {"provincial_811_default": [{"text": "811 default"}],}}


class ValidateNewAssessmentFormTest(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateNewAssessmentForm()
        self.form_name = FORM_NAME
        self.domain = DOMAIN

    def test_severe_symptoms(self):
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.SEVERE),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(PROVINCE_SLOT, SKIP_SLOT_PLACEHOLDER),
            SlotSet(AGE_OVER_65_SLOT, SKIP_SLOT_PLACEHOLDER),
            SlotSet(HAS_FEVER_SLOT, SKIP_SLOT_PLACEHOLDER),
            SlotSet(MODERATE_SYMPTOMS_SLOT, SKIP_SLOT_PLACEHOLDER),
            SlotSet(HAS_COUGH_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]
        self.check_slot_value_accepted(
            SEVERE_SYMPTOMS_SLOT, True, extra_events=extra_events
        )

    def test_no_severe_symptoms(self):
        self.check_slot_value_accepted(SEVERE_SYMPTOMS_SLOT, False)

    def test_valid_province_code_default(self):
        extra_events = [SlotSet(PROVINCIAL_811_SLOT, "811 default")]
        self.check_slot_value_accepted(PROVINCE_SLOT, "bc", extra_events=extra_events)

    def test_invalid_province_code(self):
        self.check_slot_value_rejected(PROVINCE_SLOT, "qg")

    def test_age_over_65_true(self):
        self.check_slot_value_accepted(AGE_OVER_65_SLOT, True)

    def test_age_over_65_false(self):
        self.check_slot_value_accepted(AGE_OVER_65_SLOT, False)

    def test_has_fever(self):
        self.check_slot_value_accepted(HAS_FEVER_SLOT, True)

    def test_has_no_fever(self):
        self.check_slot_value_accepted(HAS_FEVER_SLOT, False)

    def test_moderate_symptoms(self):
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_COUGH_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]
        self.check_slot_value_accepted(
            MODERATE_SYMPTOMS_SLOT, True, extra_events=extra_events
        )

    def test_no_moderate_symptoms(self):
        templates = ["utter_moderate_symptoms_false"]
        self.check_slot_value_accepted(
            MODERATE_SYMPTOMS_SLOT, False, templates=templates
        )

    def test_has_cough(self):
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
        ]
        self.check_slot_value_accepted(HAS_COUGH_SLOT, True, extra_events=extra_events)

    def test_has_no_cough_with_fever(self):
        previous_slots = {HAS_FEVER_SLOT: True}
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
        ]
        self.check_slot_value_accepted(
            HAS_COUGH_SLOT,
            False,
            extra_events=extra_events,
            previous_slots=previous_slots,
        )

    def test_has_no_cough_no_fever(self):
        previous_slots = {HAS_FEVER_SLOT: False}
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.NONE),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
        ]
        self.check_slot_value_accepted(
            HAS_COUGH_SLOT,
            False,
            extra_events=extra_events,
            previous_slots=previous_slots,
        )
