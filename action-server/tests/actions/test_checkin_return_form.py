from typing import Any, Dict, Text

from rasa_sdk import Tracker
from rasa_sdk.events import Form, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.assessment_common import AssessmentCommon
from covidflow.actions.checkin_return_form import FORM_NAME, CheckinReturnForm
from covidflow.actions.constants import (
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

from .form_helper import FormTestCase

DOMAIN = {
    "responses": {
        "provincial_811_qc": [{"text": "811 qc"}],
        "provincial_811_default": [{"text": "811 default"}],
    }
}


def validate_province(
    value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> Dict[Text, Any]:
    # real domain should be passed in real form, overwritted here to insert test-specific keys
    return AssessmentCommon.validate_province(value, DOMAIN)


class TestCheckinReturnForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = CheckinReturnForm()
        self.form.validate_province = validate_province

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(tracker)

        self.assert_events(
            [Form(FORM_NAME), SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT)]
        )

        self.assert_templates(
            ["utter_returning_for_checkin", "utter_ask_severe_symptoms"]
        )

    def test_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT}, intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.SEVERE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_not_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT}, intent="deny"
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, PROVINCE_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_province"])

    def test_collect_province(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: PROVINCE_SLOT, SEVERE_SYMPTOMS_SLOT: False,},
            intent="inform",
            entities=[{"entity": "province", "value": "qc"}],
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(PROVINCE_SLOT, "qc"),
                SlotSet(PROVINCIAL_811_SLOT, "811 qc"),
                SlotSet(REQUESTED_SLOT, AGE_OVER_65_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_collect_age_over_65(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AGE_OVER_65_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(AGE_OVER_65_SLOT, True), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),]
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_fever(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_FEVER_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, True),
                SlotSet(REQUESTED_SLOT, MODERATE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_no_fever(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_FEVER_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, False),
                SlotSet(REQUESTED_SLOT, MODERATE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_fever_moderate_symptoms(self):
        self._test_moderate_symptoms(fever=True)

    def test_no_fever_moderate_symptoms(self):
        self._test_moderate_symptoms(fever=False)

    def _test_moderate_symptoms(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(MODERATE_SYMPTOMS_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_fever_mild_symptoms(self):
        self._test_mild_symptoms(fever=True)

    def test_no_fever_mild_symptoms(self):
        self._test_mild_symptoms(fever=False)

    def _test_mild_symptoms(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(MODERATE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_has_cough"])

    def test_fever_mild_symptoms_cough(self):
        self._test_mild_symptoms_cough(fever=True)

    def test_no_fever_mild_symptoms_cough(self):
        self._test_mild_symptoms_cough(fever=False)

    def _test_mild_symptoms_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_returning_self_isolate", "utter_self_isolation_link"]
        )

    def test_fever_mild_symptoms_no_cough(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_no_fever_mild_symptoms_no_cough(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, Symptoms.NONE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])
