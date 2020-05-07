from unittest.mock import patch

from rasa_sdk.events import Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from actions.daily_ci_feel_no_change_form import (
    FEEL_WORSE_SLOT,
    FORM_NAME,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SYMPTOMS_SLOT,
    DailyCiFeelNoChangeForm,
)
from tests.form_helper import FormTestCase


class TestDailyCiFeelNoChangeForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiFeelNoChangeForm()

        self.patcher = patch("actions.daily_ci_feel_no_change_form.store_assessment")
        self.mock_store_assessment = self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def test_moderate_last_symptoms(self):
        self._test_form_activation(last_symptoms="moderate")

    def test_mild_last_symptoms(self):
        self._test_form_activation(last_symptoms="mild")

    def _test_form_activation(self, last_symptoms: str):
        tracker = self.create_tracker(
            slots={LAST_SYMPTOMS_SLOT: last_symptoms}, active_form=False
        )

        self.run_form(tracker)

        self.assert_events(
            [
                Form(FORM_NAME),
                SlotSet(FEEL_WORSE_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_daily_ci__feel_no_change__has_fever"])

    def test_moderate_last_symptoms__fever(self):
        self._test_fever(last_symptoms="moderate")

    def test_mild_last_symptoms__fever(self):
        self._test_fever(last_symptoms="mild")

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
        self._test_no_fever(last_symptoms="moderate")

    def test_mild_last_symptoms__no_fever(self):
        self._test_no_fever(last_symptoms="mild")

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

    def test_moderate_last_symptoms__fever_cough(self):
        self._test_moderate_last_symptoms__cough(fever=True)

    def test_moderate_last_symptoms__no_fever_cough(self):
        self._test_moderate_last_symptoms__cough(fever=False)

    def _test_moderate_last_symptoms__cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
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
                LAST_SYMPTOMS_SLOT: "moderate",
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
                LAST_SYMPTOMS_SLOT: "moderate",
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
                Form(None),
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
        self._test_no_diff_breathing(fever=False, cough=False, symptoms="mild")

    def _test_no_diff_breathing(self, fever: bool, cough: bool, symptoms: str = None):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="deny",
        )

        self.run_form(tracker)

        slot_set_events = [SlotSet(HAS_DIFF_BREATHING_SLOT, False)]
        if symptoms != None:
            slot_set_events.append(SlotSet(SYMPTOMS_SLOT, symptoms))

        self.assert_events(
            slot_set_events
            + [
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_no_change__acknowledge_no_diff_breathing",
                "utter_daily_ci__feel_no_change__no_diff_breathing_recommendation",
            ]
        )

    def test_mild_last_symptoms__fever_cough(self):
        self._test_mild_last_symptoms__cough(fever=True)

    def test_mild_last_symptoms__no_fever_cough(self):
        self._test_mild_last_symptoms__cough(fever=False)

    def _test_mild_last_symptoms__cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "mild",
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
                Form(None),
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

        self.mock_store_assessment.assert_called()

    def test_mild_last_symptoms__fever_no_cough(self):
        self._test_mild_last_symptoms__no_cough(fever=True)

    def test_mild_last_symptoms__no_fever_no_cough(self):
        self._test_mild_last_symptoms__no_cough(fever=False)

    def _test_mild_last_symptoms__no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "mild",
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
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_daily_ci__feel_no_change__mild_last_symptoms_recommendation",
            ]
        )

        self.mock_store_assessment.assert_called()
