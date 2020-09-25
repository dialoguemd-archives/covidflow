import pytest
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.daily_ci_feel_no_change_form import (
    FORM_NAME,
    ActionAskDailyCiFeelNoChangeFormHasCough,
    ActionAskDailyCiFeelNoChangeFormHasFever,
    ValidateDailyCiFeelNoChangeForm,
)
from covidflow.constants import (
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .action_test_helper import ActionTestCase
from .validate_action_test_helper import ValidateActionTestCase


class TestActionAskDailyCiFeelNoChangeFormHasFever(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskDailyCiFeelNoChangeFormHasFever()

    @pytest.mark.asyncio
    async def test_did_not_have_fever(self):
        tracker = self.create_tracker(slots={LAST_HAS_FEVER_SLOT: False})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(["utter_ask_daily_ci_feel_no_change_form_has_fever"])

    @pytest.mark.asyncio
    async def test_already_had_fever(self):
        tracker = self.create_tracker(slots={LAST_HAS_FEVER_SLOT: True})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(
            ["utter_ask_daily_ci_feel_no_change_form_has_fever___still"]
        )


class TestActionAskDailyCiFeelNoChangeFormHasCough(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskDailyCiFeelNoChangeFormHasCough()

    @pytest.mark.asyncio
    async def test_did_not_have_cough(self):
        tracker = self.create_tracker(slots={LAST_HAS_COUGH_SLOT: False})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(["utter_ask_daily_ci_feel_no_change_form_has_cough"])

    @pytest.mark.asyncio
    async def test_already_had_cough(self):
        tracker = self.create_tracker(slots={LAST_HAS_COUGH_SLOT: True})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(
            ["utter_ask_daily_ci_feel_no_change_form_has_cough___still"]
        )


class TestDailyCiFeelNoChangeForm(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateDailyCiFeelNoChangeForm()
        self.form_name = FORM_NAME

    @pytest.mark.asyncio
    async def test_activation(self):
        await self.check_activation()

    @pytest.mark.asyncio
    async def test_fever(self):
        templates = [
            "utter_daily_ci__acknowledge_fever",
            "utter_daily_ci__take_acetaminophen",
            "utter_daily_ci__avoid_ibuprofen",
        ]

        await self.check_slot_value_accepted(HAS_FEVER_SLOT, True, templates=templates)

    @pytest.mark.asyncio
    async def test_no_fever(self):
        templates = ["utter_daily_ci_feel_no_change_form_acknowledge_no_fever"]

        await self.check_slot_value_accepted(HAS_FEVER_SLOT, False, templates=templates)

    @pytest.mark.asyncio
    async def test_mild_last_symptoms_cough(self):
        previous_slots = {LAST_SYMPTOMS_SLOT: Symptoms.MILD}
        templates = [
            "utter_daily_ci__cough_syrup_may_help",
            "utter_daily_ci__cough_syrup_pharmacist",
            "utter_daily_ci_feel_no_change_form_mild_last_symptoms_recommendation",
        ]
        extra_events = [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_DIFF_BREATHING_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT,
            True,
            previous_slots=previous_slots,
            extra_events=extra_events,
            templates=templates,
        )

    @pytest.mark.asyncio
    async def test_mild_last_symptoms_no_cough(self):
        previous_slots = {LAST_SYMPTOMS_SLOT: Symptoms.MILD}
        templates = [
            "utter_daily_ci__acknowledge_no_cough",
            "utter_daily_ci_feel_no_change_form_mild_last_symptoms_recommendation",
        ]
        extra_events = [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_DIFF_BREATHING_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT,
            False,
            previous_slots=previous_slots,
            extra_events=extra_events,
            templates=templates,
        )

    @pytest.mark.asyncio
    async def test_moderate_last_symptoms_cough(self):
        previous_slots = {LAST_SYMPTOMS_SLOT: Symptoms.MODERATE}
        templates = [
            "utter_daily_ci__cough_syrup_may_help",
            "utter_daily_ci__cough_syrup_pharmacist",
        ]

        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT, True, previous_slots=previous_slots, templates=templates
        )

    @pytest.mark.asyncio
    async def test_moderate_last_symptoms_no_cough(self):
        previous_slots = {LAST_SYMPTOMS_SLOT: Symptoms.MODERATE}
        templates = ["utter_daily_ci__acknowledge_no_cough"]

        await self.check_slot_value_accepted(
            HAS_COUGH_SLOT, False, previous_slots=previous_slots, templates=templates
        )

    @pytest.mark.asyncio
    async def test_has_diff_breathing(self):
        templates = [
            "utter_daily_ci_feel_no_change_form_acknowledge_diff_breathing",
            "utter_daily_ci_feel_no_change_form_diff_breathing_recommendation",
        ]
        await self.check_slot_value_accepted(
            HAS_DIFF_BREATHING_SLOT, True, templates=templates
        )

    @pytest.mark.asyncio
    async def test_has_no_diff_breathing_no_other_symptom(self):
        templates = [
            "utter_daily_ci_feel_no_change_form_acknowledge_no_diff_breathing",
            "utter_daily_ci_feel_no_change_form_no_diff_breathing_recommendation",
        ]
        previous_slots = {HAS_FEVER_SLOT: False, HAS_COUGH_SLOT: False}
        extra_events = [SlotSet(SYMPTOMS_SLOT, Symptoms.MILD)]

        await self.check_slot_value_accepted(
            HAS_DIFF_BREATHING_SLOT,
            False,
            templates=templates,
            previous_slots=previous_slots,
            extra_events=extra_events,
        )

    @pytest.mark.asyncio
    async def test_has_no_diff_breathing_fever(self):
        await self._test_has_no_diff_breathing_other_symptom(True, False)

    @pytest.mark.asyncio
    async def test_has_no_diff_breathing_cough(self):
        await self._test_has_no_diff_breathing_other_symptom(False, True)

    async def _test_has_no_diff_breathing_other_symptom(self, fever: bool, cough: bool):
        templates = [
            "utter_daily_ci_feel_no_change_form_acknowledge_no_diff_breathing",
            "utter_daily_ci_feel_no_change_form_no_diff_breathing_recommendation",
        ]
        previous_slots = {HAS_FEVER_SLOT: fever, HAS_COUGH_SLOT: cough}

        await self.check_slot_value_accepted(
            HAS_DIFF_BREATHING_SLOT,
            False,
            templates=templates,
            previous_slots=previous_slots,
        )
