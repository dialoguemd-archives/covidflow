import pytest
from rasa_sdk.events import ActionExecuted, SlotSet, UserUttered
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.assessment_form import (
    FORM_NAME,
    ActionAskProvinceCode,
    ValidateNewAssessmentForm,
)
from covidflow.constants import (
    AGE_OVER_65_SLOT,
    ASSESSMENT_TYPE_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    SYMPTOMS_SLOT,
    AssessmentType,
    Symptoms,
)

from .action_test_helper import ActionTestCase
from .validate_action_test_helper import ValidateActionTestCase

DOMAIN = {"responses": {"provincial_811_default": [{"text": "811 default"}],}}


class ActionAskProvinceCodeTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskProvinceCode()

    @pytest.mark.asyncio
    async def test_ask_province_code(self):
        tracker = self.create_tracker()

        await self.run_action(tracker)

        self.assert_templates(
            ["utter_pre_ask_province_code", "utter_ask_province_code"]
        )


class ValidateNewAssessmentFormTest(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateNewAssessmentForm()
        self.form_name = FORM_NAME
        self.domain = DOMAIN

    @pytest.mark.asyncio
    async def test_activation(self):
        await self.check_activation()

    @pytest.mark.asyncio
    async def test_assessment_type_with_previous_tested_positive(self):
        tracker = self.create_tracker(
            events=[
                UserUttered(
                    "tested positive",
                    parse_data={
                        "text": "tested positive",
                        "intent": {"name": "tested_positive", "confidence": 1.0},
                        "entities": [],
                    },
                ),
                UserUttered(
                    "yes",
                    parse_data={
                        "text": "yes",
                        "intent": {"name": "affirm", "confidence": 1.0},
                        "entities": [],
                    },
                ),
                ActionExecuted(self.form_name),
                SlotSet(ASSESSMENT_TYPE_SLOT, AssessmentType.GENERIC),
            ]
        )

        await self.run_action(tracker)

        self.assert_events(
            [SlotSet(ASSESSMENT_TYPE_SLOT, AssessmentType.TESTED_POSITIVE)]
        )

        self.assert_templates([])

    @pytest.mark.asyncio
    async def test_assessment_type_valid(self):
        await self.check_slot_value_accepted(
            ASSESSMENT_TYPE_SLOT, AssessmentType.CHECKIN_RETURN
        )

    @pytest.mark.asyncio
    async def test_severe_symptoms(self):
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
        await self.check_slot_value_accepted(
            SEVERE_SYMPTOMS_SLOT, True, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_no_severe_symptoms(self):
        await self.check_slot_value_accepted(SEVERE_SYMPTOMS_SLOT, False)

    @pytest.mark.asyncio
    async def test_valid_province_code_default(self):
        extra_events = [SlotSet(PROVINCIAL_811_SLOT, "811 default")]
        await self.check_slot_value_accepted(
            PROVINCE_SLOT, "bc", extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_invalid_province_code(self):
        await self.check_slot_value_rejected(PROVINCE_SLOT, "qg")

    @pytest.mark.asyncio
    async def test_age_over_65_true(self):
        await self.check_slot_value_accepted(AGE_OVER_65_SLOT, True)

    @pytest.mark.asyncio
    async def test_age_over_65_false(self):
        await self.check_slot_value_accepted(AGE_OVER_65_SLOT, False)

    @pytest.mark.asyncio
    async def test_has_fever(self):
        await self.check_slot_value_accepted(HAS_FEVER_SLOT, True)

    @pytest.mark.asyncio
    async def test_has_no_fever(self):
        await self.check_slot_value_accepted(HAS_FEVER_SLOT, False)

    @pytest.mark.asyncio
    async def test_moderate_symptoms(self):
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_COUGH_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]
        await self.check_slot_value_accepted(
            MODERATE_SYMPTOMS_SLOT, True, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_no_moderate_symptoms(self):
        templates = ["utter_moderate_symptoms_false"]
        await self.check_slot_value_accepted(
            MODERATE_SYMPTOMS_SLOT, False, templates=templates
        )

    @pytest.mark.asyncio
    async def test_has_cough(self):
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
        ]
        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT, True, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_has_no_cough_with_fever(self):
        previous_slots = {HAS_FEVER_SLOT: True}
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
        ]
        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT,
            False,
            extra_events=extra_events,
            previous_slots=previous_slots,
        )

    @pytest.mark.asyncio
    async def test_has_no_cough_no_fever(self):
        previous_slots = {HAS_FEVER_SLOT: False}
        extra_events = [
            SlotSet(SYMPTOMS_SLOT, Symptoms.NONE),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
        ]
        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT,
            False,
            extra_events=extra_events,
            previous_slots=previous_slots,
        )
