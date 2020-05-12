from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import Form, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

from covidflow.actions.assessment_common import (
    PROVINCIAL_811_SLOT,
    AssessmentCommon,
    AssessmentSlots,
)

from .form_helper import FormTestCase

DOMAIN = {
    "responses": {
        "provincial_811_qc": [{"text": "811 qc"}],
        "provincial_811_default": [{"text": "811 default"}],
    }
}


class TestAssessmentForm(FormAction):
    def name(self) -> Text:

        return "test_assessment_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return AssessmentCommon.base_required_slots(tracker)

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return AssessmentCommon.slot_mappings(self)

    def validate_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # real domain should be passed in real form, overwritted here to insert test-specific keys
        return AssessmentCommon.validate_province(value, DOMAIN)

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return AssessmentCommon.submit(self, dispatcher, tracker, domain)


class BaseTestAssessmentForm:
    def test_provide_severe_symptoms_affirm(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: AssessmentSlots.SEVERE_SYMPTOMS}, intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.SEVERE_SYMPTOMS, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "severe"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_severe_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: AssessmentSlots.SEVERE_SYMPTOMS,}, intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.SEVERE_SYMPTOMS, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.PROVINCE),
            ],
        )

        self.assert_templates(["utter_ask_province"])

    def test_provide_province_specific_provincial_811(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                REQUESTED_SLOT: AssessmentSlots.PROVINCE,
            },
            intent="inform",
            entities=[{"entity": "province", "value": "qc"}],
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.PROVINCE, "qc"),
                SlotSet(PROVINCIAL_811_SLOT, "811 qc"),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.AGE_OVER_65),
            ],
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_provide_province_default_provincial_811(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                REQUESTED_SLOT: AssessmentSlots.PROVINCE,
            },
            intent="inform",
            entities=[{"entity": "province", "value": "bc"}],
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.PROVINCE, "bc"),
                SlotSet(PROVINCIAL_811_SLOT, "811 default"),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.AGE_OVER_65),
            ],
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_provide_age_over_65_affirm(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                REQUESTED_SLOT: AssessmentSlots.AGE_OVER_65,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.AGE_OVER_65, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.HAS_FEVER),
            ],
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_provide_age_over_65_deny(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                REQUESTED_SLOT: AssessmentSlots.AGE_OVER_65,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.AGE_OVER_65, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.HAS_FEVER),
            ],
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_provide_has_fever_affirm(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                REQUESTED_SLOT: AssessmentSlots.HAS_FEVER,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_FEVER, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.MODERATE_SYMPTOMS),
            ],
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_provide_has_fever_deny(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                REQUESTED_SLOT: AssessmentSlots.HAS_FEVER,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_FEVER, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.MODERATE_SYMPTOMS),
            ],
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_provide_moderate_symptoms_affirm(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: False,
                REQUESTED_SLOT: AssessmentSlots.MODERATE_SYMPTOMS,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.MODERATE_SYMPTOMS, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "moderate"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_moderate_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: False,
                REQUESTED_SLOT: AssessmentSlots.MODERATE_SYMPTOMS,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.MODERATE_SYMPTOMS, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.HAS_COUGH),
            ],
        )

        self.assert_templates(["utter_ask_has_cough"])

    def test_provide_has_cough_affirm_no_fever(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: False,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                REQUESTED_SLOT: AssessmentSlots.HAS_COUGH,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_COUGH, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "mild"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_affirm_has_fever(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: True,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                REQUESTED_SLOT: AssessmentSlots.HAS_COUGH,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_COUGH, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "mild"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_deny_no_fever(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: False,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                REQUESTED_SLOT: AssessmentSlots.HAS_COUGH,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_COUGH, False),
                SlotSet(AssessmentSlots.SYMPTOMS, "none"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_deny_has_fever(self):
        tracker = self.create_tracker(
            slots={
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: True,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                REQUESTED_SLOT: AssessmentSlots.HAS_COUGH,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_COUGH, False),
                SlotSet(AssessmentSlots.SYMPTOMS, "mild"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])


class TestAssessmentFormSuspect(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = TestAssessmentForm()
        self.dispatcher = CollectingDispatcher()
