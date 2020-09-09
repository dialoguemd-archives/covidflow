from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

from covidflow.actions.assessment_common import PROVINCIAL_811_SLOT, AssessmentCommon
from covidflow.constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .form_test_helper import FormTestCase

DOMAIN = {
    "responses": {
        "provincial_811_qc": [{"text": "811 qc"}],
        "provincial_811_default": [{"text": "811 default"}],
    }
}


class TestAssessmentForm(FormAction, AssessmentCommon):
    def name(self) -> Text:

        return "test_assessment_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return AssessmentCommon.base_required_slots(tracker)

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return AssessmentCommon.base_slot_mappings(self)

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return AssessmentCommon.base_submit(self, dispatcher, tracker, domain)


class BaseTestAssessmentForm:
    def test_provide_severe_symptoms_affirm(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT}, intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.SEVERE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_severe_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT,}, intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, PROVINCE_SLOT),
            ],
        )

        self.assert_templates(
            ["utter_pre_ask_province_code", "utter_ask_province_code"]
        )

    def test_provide_province_specific_provincial_811(self):
        tracker = self.create_tracker(
            slots={SEVERE_SYMPTOMS_SLOT: False, REQUESTED_SLOT: PROVINCE_SLOT,},
            intent="inform",
            entities=[{"entity": "province", "value": "qc"}],
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(PROVINCE_SLOT, "qc"),
                SlotSet(PROVINCIAL_811_SLOT, "811 qc"),
                SlotSet(REQUESTED_SLOT, AGE_OVER_65_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_provide_province_default_provincial_811(self):
        tracker = self.create_tracker(
            slots={SEVERE_SYMPTOMS_SLOT: False, REQUESTED_SLOT: PROVINCE_SLOT,},
            intent="inform",
            entities=[{"entity": "province", "value": "bc"}],
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(PROVINCE_SLOT, "bc"),
                SlotSet(PROVINCIAL_811_SLOT, "811 default"),
                SlotSet(REQUESTED_SLOT, AGE_OVER_65_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_provide_age_over_65_affirm(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                REQUESTED_SLOT: AGE_OVER_65_SLOT,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(AGE_OVER_65_SLOT, True), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),],
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_provide_age_over_65_deny(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                REQUESTED_SLOT: AGE_OVER_65_SLOT,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(AGE_OVER_65_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_provide_has_fever_affirm(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                REQUESTED_SLOT: HAS_FEVER_SLOT,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, True),
                SlotSet(REQUESTED_SLOT, MODERATE_SYMPTOMS_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_provide_has_fever_deny(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                REQUESTED_SLOT: HAS_FEVER_SLOT,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, False),
                SlotSet(REQUESTED_SLOT, MODERATE_SYMPTOMS_SLOT),
            ],
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_provide_moderate_symptoms_affirm(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MODERATE_SYMPTOMS_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MODERATE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_moderate_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MODERATE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),
            ],
        )

        self.assert_templates(["utter_moderate_symptoms_false", "utter_ask_has_cough"])

    def test_provide_has_cough_affirm_no_fever(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                MODERATE_SYMPTOMS_SLOT: False,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_affirm_has_fever(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
                MODERATE_SYMPTOMS_SLOT: False,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_deny_no_fever(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                MODERATE_SYMPTOMS_SLOT: False,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, Symptoms.NONE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_deny_has_fever(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
                MODERATE_SYMPTOMS_SLOT: False,
                REQUESTED_SLOT: HAS_COUGH_SLOT,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])


class TestAssessmentFormSuspect(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = TestAssessmentForm()
        self.dispatcher = CollectingDispatcher()
