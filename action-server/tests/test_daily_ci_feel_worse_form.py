from rasa_sdk.events import Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from actions.daily_ci_feel_worse_form import (
    FORM_NAME,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_DIFF_BREATHING_WORSENED_SLOT,
    HAS_FEVER_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    DailyCiFeelWorseForm,
)
from tests.form_helper import FormTestCase


class TestDailyCiFeelWorseForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiFeelWorseForm()

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(tracker)

        self.assert_events(
            [Form(FORM_NAME), SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT)],
        )

        self.assert_templates(["utter_ask_daily_ci__feel_worse__severe_symptoms"])

    def test_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT}, intent="affirm"
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(["utter_call_911"])

    def test_no_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT}, intent="deny"
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_worse__acknowledge_no_severe_symptoms",
                "utter_ask_daily_ci__feel_worse__has_fever",
            ]
        )

    def test_fever(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_FEVER_SLOT, SEVERE_SYMPTOMS_SLOT: False},
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_fever",
                "utter_daily_ci__take_acetaminophen",
                "utter_daily_ci__avoid_ibuprofen",
                "utter_ask_daily_ci__feel_worse__has_diff_breathing",
            ]
        )

    def test_no_fever(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_FEVER_SLOT, SEVERE_SYMPTOMS_SLOT: False},
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_worse__acknowledge_no_fever",
                "utter_ask_daily_ci__feel_worse__has_diff_breathing",
            ]
        )

    def test_fever_diff_breathing(self):
        self._test_diff_breathing(fever=True)

    def test_no_fever_diff_breathing(self):
        self._test_diff_breathing(fever=False)

    def _test_diff_breathing(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, True),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_WORSENED_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_worse__has_diff_breathing_worsened"]
        )

    def test_fever_diff_breathing_worsened(self):
        self._test_diff_breathing_worsened(fever=True)

    def test_no_fever_diff_breathing_worsened(self):
        self._test_diff_breathing_worsened(fever=False)

    def _test_diff_breathing_worsened(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_WORSENED_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: True,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_WORSENED_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_worse__diff_breathing_worsened_recommendation_1",
                "utter_daily_ci__feel_worse__diff_breathing_worsened_recommendation_2",
            ]
        )

    def test_fever_diff_breathing_not_worsened(self):
        self._test_diff_breathing_not_worsened(fever=True)

    def test_no_fever_diff_breathing_not_worsened(self):
        self._test_diff_breathing_not_worsened(fever=False)

    def _test_diff_breathing_not_worsened(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_WORSENED_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: True,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_WORSENED_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_worse__diff_breathing_not_worsened_recommendation_1",
                "utter_daily_ci__feel_worse__diff_breathing_not_worsened_recommendation_2",
            ]
        )

    def test_fever_no_diff_breathing(self):
        self._test_no_diff_breathing(fever=True)

    def test_no_fever_no_diff_breathing(self):
        self._test_no_diff_breathing(fever=False)

    def _test_no_diff_breathing(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_worse__acknowledge_no_diff_breathing",
                "utter_ask_daily_ci__feel_worse__has_cough",
            ]
        )

    def test_fever_no_diff_breathing_cough(self):
        self._test_no_diff_breathing_cough(fever=True)

    def test_no_fever_no_diff_breathing_cough(self):
        self._test_no_diff_breathing_cough(fever=False)

    def _test_no_diff_breathing_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(HAS_COUGH_SLOT, True), Form(None), SlotSet(REQUESTED_SLOT, None),],
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
            ]
        )

    def test_fever_no_diff_breathing_no_cough(self):
        self._test_no_diff_breathing_no_cough(fever=True)

    def test_no_fever_no_diff_breathing_no_cough(self):
        self._test_no_diff_breathing_no_cough(fever=False)

    def _test_no_diff_breathing_no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_daily_ci__feel_worse__no_cough_recommendation",
            ]
        )
