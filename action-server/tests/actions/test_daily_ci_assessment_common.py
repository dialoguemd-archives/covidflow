import pytest
from asynctest import patch
from rasa_sdk.events import SlotSet

from covidflow.actions.daily_ci_assessment_common import ActionSubmitDailyCiAssessment
from covidflow.constants import (
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .action_test_helper import INITIAL_SLOT_VALUES, ActionTestCase

LAST_SYMPTOMS = {
    LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
    LAST_HAS_FEVER_SLOT: True,
    LAST_HAS_COUGH_SLOT: False,
    LAST_HAS_DIFF_BREATHING_SLOT: True,
}

NEW_SYMPTOMS = {
    SYMPTOMS_SLOT: Symptoms.MILD,
    HAS_FEVER_SLOT: True,
    HAS_DIFF_BREATHING_SLOT: False,
}


class ActionSubmitDailyCiAssessmentTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionSubmitDailyCiAssessment()

        self.patcher = patch(
            "covidflow.actions.daily_ci_assessment_common.save_assessment"
        )
        self.mock_save_assessment = self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    @pytest.mark.asyncio
    async def test_saves_with_last_values_if_new_ones_empty(self):
        tracker = self.create_tracker(slots=LAST_SYMPTOMS)

        await self.run_action(tracker)

        self.assert_events(
            [
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                SlotSet(HAS_FEVER_SLOT, True),
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(HAS_DIFF_BREATHING_SLOT, True),
            ]
        )

        self.assert_templates([])

        self.mock_save_assessment.assert_called_once_with(
            {
                **INITIAL_SLOT_VALUES,
                **LAST_SYMPTOMS,
                SYMPTOMS_SLOT: Symptoms.MODERATE,
                HAS_FEVER_SLOT: True,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: True,
            }
        )

    @pytest.mark.asyncio
    async def test_saves_with_new_values_overrides(self):
        tracker = self.create_tracker(slots={**LAST_SYMPTOMS, **NEW_SYMPTOMS})

        await self.run_action(tracker)

        self.assert_events(
            [SlotSet(SELF_ASSESS_DONE_SLOT, True), SlotSet(HAS_COUGH_SLOT, False)]
        )

        self.assert_templates([])

        self.mock_save_assessment.assert_called_once_with(
            {
                **INITIAL_SLOT_VALUES,
                **LAST_SYMPTOMS,
                **NEW_SYMPTOMS,
                HAS_COUGH_SLOT: False,
            }
        )

    @pytest.mark.asyncio
    @patch("covidflow.actions.daily_ci_assessment_common.cancel_reminder")
    async def test_cancels_when_severe_symptoms(self, mock_cancel_reminder):
        tracker = self.create_tracker(
            slots={**LAST_SYMPTOMS, SYMPTOMS_SLOT: Symptoms.SEVERE}
        )

        await self.run_action(tracker)

        self.assert_events(
            [
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(HAS_FEVER_SLOT, True),
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(HAS_DIFF_BREATHING_SLOT, True),
            ]
        )

        self.assert_templates([])

        self.mock_save_assessment.assert_called_once()

        mock_cancel_reminder.assert_called_once()
