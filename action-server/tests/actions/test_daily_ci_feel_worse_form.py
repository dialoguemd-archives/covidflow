from unittest.mock import patch

from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.daily_ci_feel_worse_form import (
    FORM_NAME,
    HAS_DIFF_BREATHING_WORSENED_SLOT,
    DailyCiFeelWorseForm,
)
from covidflow.constants import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .form_test_helper import FormTestCase

DOMAIN = {
    "responses": {
        "utter_ask_daily_ci__feel_worse__has_diff_breathing_worsened_error": [
            {"text": ""}
        ],
    }
}


class TestDailyCiFeelWorseForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiFeelWorseForm()

        self.patcher = patch(
            "covidflow.actions.daily_ci_assessment_common.save_assessment"
        )
        self.mock_save_assessment = self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def test_form_activation(self):
        tracker = self.create_tracker(active_loop=False)

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(FEEL_WORSE_SLOT, True),
                SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_daily_ci__feel_worse__severe_symptoms"])

    @patch("covidflow.actions.daily_ci_assessment_common.cancel_reminder")
    def test_severe_symptoms(self, mock_cancel_reminder):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                LAST_HAS_FEVER_SLOT: True,
                LAST_HAS_DIFF_BREATHING_SLOT: True,
                LAST_HAS_COUGH_SLOT: True,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.SEVERE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(HAS_FEVER_SLOT, True),
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(HAS_DIFF_BREATHING_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

        mock_cancel_reminder.assert_called_once

    def test_no_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT}, intent="deny"
        )

        self.run_form(tracker, DOMAIN)

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

    def test_severe_symptoms_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                LAST_HAS_FEVER_SLOT: True,
                LAST_HAS_DIFF_BREATHING_SLOT: True,
                LAST_HAS_COUGH_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, None),
                SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_daily_ci__feel_worse__severe_symptoms_error"])

    def test_fever(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_FEVER_SLOT, SEVERE_SYMPTOMS_SLOT: False},
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

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

        self.run_form(tracker, DOMAIN)

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

    def test_fever_error(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_FEVER_SLOT, SEVERE_SYMPTOMS_SLOT: False},
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_worse__has_fever_error",]
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

        self.run_form(tracker, DOMAIN)

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
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                LAST_HAS_COUGH_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: True,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_WORSENED_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                SlotSet(HAS_COUGH_SLOT, False),
                ActiveLoop(None),
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
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                LAST_HAS_COUGH_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: True,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_WORSENED_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                SlotSet(HAS_COUGH_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_worse__diff_breathing_not_worsened_recommendation_1",
                "utter_daily_ci__feel_worse__diff_breathing_not_worsened_recommendation_2",
            ]
        )

    def test_diff_breathing_worsened_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_WORSENED_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                LAST_HAS_COUGH_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: True,
                HAS_DIFF_BREATHING_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_WORSENED_SLOT, None),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_WORSENED_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_worse__has_diff_breathing_worsened_error",]
        )

    def test_fever_no_diff_breathing(self):
        self._test_no_diff_breathing(fever=True)

    def test_no_fever_no_diff_breathing(self):
        self._test_no_diff_breathing(fever=False)

    def _test_no_diff_breathing(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

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

    def test_diff_breathing_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_DIFF_BREATHING_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, None),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_worse__has_diff_breathing_error"]
        )

    def test_fever_no_diff_breathing_cough(self):
        self._test_no_diff_breathing_cough(fever=True)

    def test_no_fever_no_diff_breathing_cough(self):
        self._test_no_diff_breathing_cough(fever=False)

    def _test_no_diff_breathing_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
            ]
        )

        self.mock_save_assessment.assert_called()

    def test_fever_no_diff_breathing_no_cough(self):
        self._test_no_diff_breathing_no_cough(fever=True)

    def test_no_fever_no_diff_breathing_no_cough(self):
        self._test_no_diff_breathing_no_cough(fever=False)

    def _test_no_diff_breathing_no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_DIFF_BREATHING_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_daily_ci__feel_worse__no_cough_recommendation",
            ]
        )

        self.mock_save_assessment.assert_called()

    def test_cough_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LAST_SYMPTOMS_SLOT: Symptoms.MODERATE,
                SEVERE_SYMPTOMS_SLOT: False,
                HAS_FEVER_SLOT: True,
                HAS_DIFF_BREATHING_SLOT: False,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_COUGH_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),],
        )

        self.assert_templates(
            ["utter_ask_daily_ci__feel_worse__has_cough_error",]
        )
