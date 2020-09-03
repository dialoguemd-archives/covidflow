from unittest.mock import patch

from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.daily_ci_feel_no_change_form import (
    FORM_NAME,
    DailyCiFeelNoChangeForm,
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


class TestDailyCiFeelNoChangeForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiFeelNoChangeForm()

        self.patcher = patch(
            "covidflow.actions.daily_ci_assessment_common.save_assessment"
        )
        self.mock_save_assessment = self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def test_moderate_last_symptoms(self):
        self._test_form_activation(last_symptoms=Symptoms.MODERATE)

    def test_mild_last_symptoms(self):
        self._test_form_activation(last_symptoms=Symptoms.MILD)

    def _test_form_activation(self, last_symptoms: str):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: last_symptoms}, active_loop=False
        )

        self.run_form(tracker)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(FEEL_WORSE_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_daily_ci__feel_no_change__has_fever"])

    def test_moderate_last_symptoms__fever(self):
        self._test_fever(last_symptoms=Symptoms.MODERATE)

    def test_mild_last_symptoms__fever(self):
        self._test_fever(last_symptoms=Symptoms.MILD)

    def _test_fever(self, last_symptoms: str):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: last_symptoms, REQUESTED_SLOT: HAS_FEVER_SLOT},
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, True), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),],
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_fever",
                "utter_daily_ci__take_acetaminophen",
                "utter_daily_ci__avoid_ibuprofen",
                "utter_ask_daily_ci__feel_no_change__has_cough",
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

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, False), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_no_change__acknowledge_no_fever",
                "utter_ask_daily_ci__feel_no_change__has_cough",
            ]
        )

    def test_fever_error(self):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: Symptoms.MILD, REQUESTED_SLOT: HAS_FEVER_SLOT},
            text="anything",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_no_change__has_fever_error",]
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

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
                "utter_ask_daily_ci__feel_no_change__has_diff_breathing",
            ]
        )

    def test_moderate_last_symptoms__fever_no_cough(self):
        self._test_moderate_last_symptoms__no_cough(fever=True)

    def test_moderate_last_symptoms__no_fever_no_cough(self):
        self._test_moderate_last_symptoms__no_cough(fever=False)

    def _test_moderate_last_symptoms__no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_ask_daily_ci__feel_no_change__has_diff_breathing",
            ]
        )

    def test_cough_error(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(HAS_COUGH_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_no_change__has_cough_error",]
        )

    def test_moderate_last_symptoms__fever_cough__diff_breathing(self):
        self._test_diff_breathing(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__diff_breathing(self):
        self._test_diff_breathing(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__diff_breathing(self):
        self._test_diff_breathing(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__diff_breathing(self):
        self._test_diff_breathing(fever=False, cough=False)

    def _test_diff_breathing(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_no_change__acknowledge_diff_breathing",
                "utter_daily_ci__feel_no_change__diff_breathing_recommendation",
            ]
        )

    def test_moderate_last_symptoms__fever_cough__no_diff_breathing(self):
        self._test_no_diff_breathing(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__no_diff_breathing(self):
        self._test_no_diff_breathing(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__no_diff_breathing(self):
        self._test_no_diff_breathing(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__no_diff_breathing(self):
        self._test_no_diff_breathing(fever=False, cough=False, symptoms=Symptoms.MILD)

    def _test_no_diff_breathing(self, fever: bool, cough: bool, symptoms: str = None):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="deny",
        )

        self.run_form(tracker)

        slot_set_events = [SlotSet(HAS_DIFF_BREATHING_SLOT, False)]
        if symptoms != None:
            slot_set_events += [
                SlotSet(SYMPTOMS_SLOT, symptoms),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
            ]
        else:
            slot_set_events += [
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
            ]

        self.assert_events(
            slot_set_events + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_no_change__acknowledge_no_diff_breathing",
                "utter_daily_ci__feel_no_change__no_diff_breathing_recommendation",
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

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, None),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_no_change__has_diff_breathing_error",]
        )

    def test_mild_last_symptoms__fever_cough(self):
        self._test_mild_last_symptoms__cough(fever=True)

    def test_mild_last_symptoms__no_fever_cough(self):
        self._test_mild_last_symptoms__cough(fever=False)

    def _test_mild_last_symptoms__cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: fever,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
                "utter_daily_ci__feel_no_change__mild_last_symptoms_recommendation",
            ]
        )

        self.mock_save_assessment.assert_called()

    def test_mild_last_symptoms__fever_no_cough(self):
        self._test_mild_last_symptoms__no_cough(fever=True)

    def test_mild_last_symptoms__no_fever_no_cough(self):
        self._test_mild_last_symptoms__no_cough(fever=False)

    def _test_mild_last_symptoms__no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: Symptoms.MILD,
                LAST_HAS_DIFF_BREATHING_SLOT: False,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_daily_ci__feel_no_change__mild_last_symptoms_recommendation",
            ]
        )

        self.mock_save_assessment.assert_called()
