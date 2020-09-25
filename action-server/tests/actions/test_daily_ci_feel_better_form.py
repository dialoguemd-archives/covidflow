import pytest
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.daily_ci_feel_better_form import (
    FORM_NAME,
    HAS_OTHER_MILD_SYMPTOMS_SLOT,
    IS_SYMPTOM_FREE_SLOT,
    ActionAskDailyCiFeelBetterFormHasCough,
    ActionAskDailyCiFeelBetterFormHasOtherMildSymptoms,
    ValidateDailyCiFeelBetterForm,
)
from covidflow.constants import (
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_SYMPTOMS_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .action_test_helper import ActionTestCase
from .validate_action_test_helper import ValidateActionTestCase


class TestActionAskDailyCiFeelBetterFormHasCough(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskDailyCiFeelBetterFormHasCough()

    @pytest.mark.asyncio
    async def test_did_not_have_cough(self):
        tracker = self.create_tracker(slots={LAST_HAS_COUGH_SLOT: False})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(["utter_ask_daily_ci_feel_better_form_has_cough"])

    @pytest.mark.asyncio
    async def test_already_had_cough(self):
        tracker = self.create_tracker(slots={LAST_HAS_COUGH_SLOT: True})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(["utter_ask_daily_ci_feel_better_form_has_cough___still"])


class TestActionAskDailyCiFeelBetterFormHasOtherMildSymptoms(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskDailyCiFeelBetterFormHasOtherMildSymptoms()

    @pytest.mark.asyncio
    async def test_last_symptoms_moderate(self):
        tracker = self.create_tracker(slots={LAST_SYMPTOMS_SLOT: Symptoms.MODERATE})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(
            [
                "utter_ask_daily_ci_feel_better_form_has_other_mild_symptoms___with_acknowledge"
            ]
        )

    @pytest.mark.asyncio
    async def test_last_symptoms_mild(self):
        tracker = self.create_tracker(slots={LAST_SYMPTOMS_SLOT: Symptoms.MILD})

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(
            ["utter_ask_daily_ci_feel_better_form_has_other_mild_symptoms"]
        )


class TestValidateDailyCiFeelBetterForm(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateDailyCiFeelBetterForm()
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
        templates = ["utter_daily_ci_feel_better_acknowledge_no_fever"]

        await self.check_slot_value_accepted(HAS_FEVER_SLOT, False, templates=templates)

    @pytest.mark.asyncio
    async def test_mild_last_symptoms_cough(self):
        previous_slots = {LAST_SYMPTOMS_SLOT: Symptoms.MILD}
        templates = [
            "utter_daily_ci__cough_syrup_may_help",
            "utter_daily_ci__cough_syrup_pharmacist",
        ]
        extra_events = [SlotSet(HAS_DIFF_BREATHING_SLOT, SKIP_SLOT_PLACEHOLDER)]

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
        templates = ["utter_daily_ci__acknowledge_no_cough"]
        extra_events = [SlotSet(HAS_DIFF_BREATHING_SLOT, SKIP_SLOT_PLACEHOLDER)]

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
            "utter_daily_ci_feel_better_breathing_difficulty_recommendation_1",
            "utter_daily_ci_feel_better_breathing_difficulty_recommendation_2",
        ]
        extra_events = [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, SKIP_SLOT_PLACEHOLDER),
            SlotSet(IS_SYMPTOM_FREE_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            HAS_DIFF_BREATHING_SLOT,
            True,
            extra_events=extra_events,
            templates=templates,
        )

    @pytest.mark.asyncio
    async def test_has_no_diff_breathing(self):
        extra_events = [SlotSet(SYMPTOMS_SLOT, Symptoms.MILD)]

        await self.check_slot_value_accepted(
            HAS_DIFF_BREATHING_SLOT, False, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_has_other_mild_symptoms(self):
        await self._test_has_some_mild_symptom(False, False, True)

    @pytest.mark.asyncio
    async def test_has_no_other_mild_symptoms_has_fever(self):
        await self._test_has_some_mild_symptom(True, False, False)

    @pytest.mark.asyncio
    async def test_has_no_other_mild_symptoms_has_cough(self):
        await self._test_has_some_mild_symptom(False, True, False)

    async def _test_has_some_mild_symptom(
        self, fever: bool, cough: bool, other_mild: bool
    ):
        previous_slots = {HAS_FEVER_SLOT: fever, HAS_COUGH_SLOT: cough}
        templates = [
            "utter_daily_ci_feel_better_form_has_other_mild_symptoms_recommendation"
        ]
        extra_events = [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(IS_SYMPTOM_FREE_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            HAS_OTHER_MILD_SYMPTOMS_SLOT,
            other_mild,
            previous_slots=previous_slots,
            extra_events=extra_events,
            templates=templates,
        )

    @pytest.mark.asyncio
    async def test_has_no_listed_mild_symptoms(self):
        previous_slots = {HAS_FEVER_SLOT: False, HAS_COUGH_SLOT: False}

        await self.check_slot_value_accepted(
            HAS_OTHER_MILD_SYMPTOMS_SLOT, False, previous_slots=previous_slots
        )

    @pytest.mark.asyncio
    async def test_is_symptom_free(self):
        extra_events = [SlotSet(SYMPTOMS_SLOT, Symptoms.NONE)]
        await self.check_slot_value_accepted(
            IS_SYMPTOM_FREE_SLOT, True, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_is_not_symptom_free(self):
        templates = [
            "utter_daily_ci_feel_better_form_has_other_mild_symptoms_still_sick_recommendation"
        ]
        await self.check_slot_value_accepted(
            IS_SYMPTOM_FREE_SLOT, False, templates=templates
        )
