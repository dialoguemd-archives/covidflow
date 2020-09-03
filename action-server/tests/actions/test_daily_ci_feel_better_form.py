from unittest.mock import patch

from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.daily_ci_feel_better_form import (
    FORM_NAME,
    HAS_OTHER_MILD_SYMPTOMS_SLOT,
    IS_SYMPTOM_FREE_SLOT,
    DailyCiFeelBetterForm,
)
from covidflow.constants import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_SYMPTOMS_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .form_test_helper import FormTestCase

DOMAIN = {
    "responses": {
        "utter_ask_daily_ci__feel_better__has_other_mild_symptoms_error": [
            {"text": ""}
        ],
        "utter_ask_daily_ci__feel_better__is_symptom_free_error": [{"text": ""}],
    }
}


class TestDailyCiFeelBetterForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiFeelBetterForm()

        self.patcher = patch(
            "covidflow.actions.daily_ci_assessment_common.save_assessment"
        )
        self.mock_save_assessment = self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def test_moderate(self):
        self._test_form_activation(last_symptoms=Symptoms.MODERATE)

    def test_mild(self):
        self._test_form_activation(last_symptoms=Symptoms.MILD)

    def _test_form_activation(self, last_symptoms: str):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: last_symptoms}, active_loop=False
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(FEEL_WORSE_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__acknowledge",
                "utter_ask_daily_ci__feel_better__has_fever",
            ]
        )

    def test_moderate_last_symptoms__fever(self):
        self._test_fever(last_symptoms=Symptoms.MODERATE)

    def test_mild_last_symptoms__fever(self):
        self._test_fever(last_symptoms=Symptoms.MILD)

    def _test_fever(self, last_symptoms: str):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: last_symptoms, REQUESTED_SLOT: HAS_FEVER_SLOT},
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, True), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT)]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_fever",
                "utter_daily_ci__take_acetaminophen",
                "utter_daily_ci__avoid_ibuprofen",
                "utter_ask_daily_ci__feel_better__has_cough",
            ]
        )

    def test_moderate_last_symptoms__no_fever(self):
        self._test_no_fever(last_symptoms=Symptoms.MODERATE)

    def test_mild_last_symptoms__no_fever(self):
        self._test_no_fever(last_symptoms=Symptoms.MILD)

    def _test_no_fever(self, last_symptoms: str):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: last_symptoms, REQUESTED_SLOT: HAS_FEVER_SLOT},
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, False), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT)]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__acknowledge_no_fever",
                "utter_ask_daily_ci__feel_better__has_cough",
            ]
        )

    def test_fever_error(self):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: Symptoms.MILD, REQUESTED_SLOT: HAS_FEVER_SLOT},
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT)]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_better__has_fever_error",]
        )

    def test_moderate_last_symptoms__fever_cough(self):
        self._test_moderate_last_symptoms__cough(fever=True)

    def test_moderate_last_symptoms__no_fever_cough(self):
        self._test_moderate_last_symptoms__cough(fever=False)

    def _test_moderate_last_symptoms__cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: fever,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
                "utter_ask_daily_ci__feel_better__has_diff_breathing",
            ]
        )

    def test_moderate_last_symptoms__fever_no_cough(self):
        self._test_moderate_last_symptoms__no_cough(fever=True)

    def test_moderate_last_symptoms__no_fever_no_cough(self):
        self._test_moderate_last_symptoms__no_cough(fever=False)

    def _test_moderate_last_symptoms__no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_ask_daily_ci__feel_better__has_diff_breathing",
            ]
        )

    def test_cough_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                HAS_FEVER_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_COUGH_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_better__has_cough_error",]
        )

    def test_moderate_last_symptoms__fever_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=False, cough=False)

    def _test_moderate_last_symptoms__diff_breathing(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__breathing_difficulty_recommendation_1",
                "utter_daily_ci__feel_better__breathing_difficulty_recommendation_2",
            ]
        )

    def test_moderate_last_symptoms__fever_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=False, cough=False)

    def _test_moderate_last_symptoms__no_diff_breathing(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_ask_daily_ci__feel_better__has_other_mild_symptoms_with_acknowledge"
            ]
        )

    def test_diff_breathing_error(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                HAS_FEVER_SLOT: True,
                HAS_COUGH_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, None),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_better__has_diff_breathing_error"]
        )

    def test_moderate_last_symptoms__fever_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=False, cough=False)

    def _test_moderate_last_symptoms__mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

    def test_moderate_last_symptoms__fever_cough__no_other_mild(self):
        self._test_moderate_last_symptoms__no_other_mild(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__no_other_mild(self):
        self._test_moderate_last_symptoms__no_other_mild(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__no_other_mild(self):
        self._test_moderate_last_symptoms__no_other_mild(fever=True, cough=False)

    def _test_moderate_last_symptoms__no_other_mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

    def test_moderate_last_symptoms__no_fever_no_cough__no_other_mild(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, IS_SYMPTOM_FREE_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_daily_ci__feel_better__is_symptom_free"])

    def test_other_mild_symptoms_error(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, None),
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_better__has_other_mild_symptoms_error"]
        )

    def test_moderate_last_symptoms__is_symptom_free_afffirm(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.NONE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_moderate_last_symptoms__is_symptoms_free_deny(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__has_other_mild_symptoms_still_sick_recommendation"
            ]
        )

    def test_moderate_last_symptoms__is_symptom_free_error(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="something_else",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, None),
                SlotSet(REQUESTED_SLOT, IS_SYMPTOM_FREE_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_better__is_symptom_free_error"]
        )

    def test_mild_last_symptoms__fever_cough(self):
        self._test_other_mild_last_symptoms__cough(fever=True)

    def test_mild_last_symptoms__no_fever_cough(self):
        self._test_other_mild_last_symptoms__cough(fever=False)

    def _test_other_mild_last_symptoms__cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: fever,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
                "utter_ask_daily_ci__feel_better__has_other_mild_symptoms",
            ]
        )

    def test_mild_last_symptoms__fever_no_cough(self):
        self._test_other_mild_last_symptoms__no_cough(fever=True)

    def test_mild_last_symptoms__no_fever_no_cough(self):
        self._test_other_mild_last_symptoms__no_cough(fever=False)

    def _test_other_mild_last_symptoms__no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_ask_daily_ci__feel_better__has_other_mild_symptoms",
            ]
        )

    def test_mild_last_symptoms__fever_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=True, cough=True)

    def test_mild_last_symptoms__no_fever_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=False, cough=True)

    def test_mild_last_symptoms__fever_no_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=True, cough=False)

    def test_mild_last_symptoms__no_fever_no_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=False, cough=False)

    def _test_mild_last_symptoms__other_mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

        self.mock_save_assessment.assert_called()

    def test_mild_last_symptoms__fever_cough__no_other_mild(self):
        self._test_mild_last_symptoms__no_other_mild(fever=True, cough=True)

    def test_mild_last_symptoms__no_fever_cough__no_other_mild(self):
        self._test_mild_last_symptoms__no_other_mild(fever=False, cough=True)

    def test_mild_last_symptoms__fever_no_cough__no_other_mild(self):
        self._test_mild_last_symptoms__no_other_mild(fever=True, cough=False)

    def _test_mild_last_symptoms__no_other_mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

        self.mock_save_assessment.assert_called()

    def test_mild_last_symptoms__is_symptom_free_affirm(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.NONE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

        self.mock_save_assessment.assert_called()

    def test_mild_last_symptoms__is_symptom_free_deny(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__has_other_mild_symptoms_still_sick_recommendation"
            ]
        )

        self.mock_save_assessment.assert_called()

    def test_mild_last_symptoms__is_symptom_free_error(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
            },
            intent="something_else",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, None),
                SlotSet(REQUESTED_SLOT, IS_SYMPTOM_FREE_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_better__is_symptom_free_error"]
        )
