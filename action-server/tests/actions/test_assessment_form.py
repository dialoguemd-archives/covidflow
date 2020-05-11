from typing import Any, Dict, Text

from rasa_sdk import Tracker
from rasa_sdk.events import Form, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.assessment_common import (
    PROVINCIAL_811_SLOT,
    AssessmentCommon,
    AssessmentSlots,
)
from covidflow.actions.assessment_form import (
    CONTACT_RISK_SLOT,
    FORM_NAME,
    AssessmentForm,
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


class TestAssessmentForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = AssessmentForm()
        self.form.validate_province = validate_province

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(tracker)

        self.assert_events(
            [Form(FORM_NAME), SlotSet(REQUESTED_SLOT, AssessmentSlots.SEVERE_SYMPTOMS)]
        )

        self.assert_templates(["utter_ask_severe_symptoms"])

    def test_severe_symptoms(self):
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
            ]
        )

        self.assert_templates([])

    def test_not_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: AssessmentSlots.SEVERE_SYMPTOMS}, intent="deny"
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.SEVERE_SYMPTOMS, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.PROVINCE),
            ]
        )

        self.assert_templates(["utter_ask_province"])

    def test_collect_province(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.PROVINCE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
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
            ]
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_collect_age_over_65(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.AGE_OVER_65,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.AGE_OVER_65, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.HAS_FEVER),
            ]
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_fever(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.HAS_FEVER,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_FEVER, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.MODERATE_SYMPTOMS),
            ]
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_no_fever(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.HAS_FEVER,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_FEVER, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.MODERATE_SYMPTOMS),
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
                REQUESTED_SLOT: AssessmentSlots.MODERATE_SYMPTOMS,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.MODERATE_SYMPTOMS, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.LIVES_ALONE),
            ]
        )

        self.assert_templates(
            ["utter_moderate_symptoms_self_isolate", "utter_ask_lives_alone"]
        )

    def test_fever_moderate_symptoms_lives_alone(self):
        self._test_moderate_symptoms_lives_alone(fever=True)

    def test_no_fever_moderate_symptoms_lives_alone(self):
        self._test_moderate_symptoms_lives_alone(fever=False)

    def _test_moderate_symptoms_lives_alone(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: True,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.LIVES_ALONE, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "moderate"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_dont_leave_home", "utter_self_isolation_link"])

    def test_fever_moderate_symptoms_not_lives_alone(self):
        self._test_moderate_symptoms_not_lives_alone(fever=True)

    def test_no_fever_moderate_symptoms_not_lives_alone(self):
        self._test_moderate_symptoms_not_lives_alone(fever=False)

    def _test_moderate_symptoms_not_lives_alone(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: True,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.LIVES_ALONE, False),
                SlotSet(AssessmentSlots.SYMPTOMS, "moderate"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_stay_separate_room",
                "utter_distance_clean_surfaces",
                "utter_wear_mask_same_room",
                "utter_self_isolation_link",
            ]
        )

    def test_fever_mild_symptoms(self):
        self._test_mild_symptoms(fever=True)

    def test_no_fever_mild_symptoms(self):
        self._test_mild_symptoms(fever=False)

    def _test_mild_symptoms(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.MODERATE_SYMPTOMS,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.MODERATE_SYMPTOMS, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.HAS_COUGH),
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
                REQUESTED_SLOT: AssessmentSlots.HAS_COUGH,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_COUGH, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.LIVES_ALONE),
            ]
        )

        self.assert_templates(
            ["utter_mild_symptoms_self_isolate", "utter_ask_lives_alone"]
        )

    def test_fever_mild_symptoms_no_cough(self):
        self._test_mild_symptoms_no_cough(fever=True)

    def test_no_fever_mild_symptoms_no_cough(self):
        self._test_mild_symptoms_no_cough(fever=False)

    def _test_mild_symptoms_no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.HAS_COUGH,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.HAS_COUGH, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.CONTACT),
            ]
        )

        self.assert_templates(["utter_ask_contact"])

    def test_fever_mild_symptoms_no_cough_contact(self):
        self._test_mild_symptoms_no_cough_contact(fever=True)

    def test_no_fever_mild_symptoms_no_cough_contact(self):
        self._test_mild_symptoms_no_cough_contact(fever=False)

    def _test_mild_symptoms_no_cough_contact(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.CONTACT,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.CONTACT, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.LIVES_ALONE),
            ]
        )

        self.assert_templates(
            ["utter_contact_risk_self_isolate", "utter_ask_lives_alone"]
        )

    def test_fever_mild_symptoms_no_cough_contact_lives_alone(self):
        self._test_mild_symptoms_no_cough_contact_lives_alone(fever=True)

    def test_no_fever_mild_symptoms_no_cough_contact_lives_alone(self):
        self._test_mild_symptoms_no_cough_contact_lives_alone(fever=False)

    def _test_mild_symptoms_no_cough_contact_lives_alone(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
                AssessmentSlots.CONTACT: True,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.LIVES_ALONE, True),
                SlotSet(CONTACT_RISK_SLOT, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "none"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_dont_leave_home", "utter_self_isolation_link"])

    def test_fever_mild_symptoms_no_cough_contact_not_lives_alone(self):
        self._test_mild_symptoms_no_cough_contact_not_lives_alone(fever=True)

    def test_no_fever_mild_symptoms_no_cough_contact_not_lives_alone(self):
        self._test_mild_symptoms_no_cough_contact_not_lives_alone(fever=False)

    def _test_mild_symptoms_no_cough_contact_not_lives_alone(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
                AssessmentSlots.CONTACT: True,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.LIVES_ALONE, False),
                SlotSet(CONTACT_RISK_SLOT, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "none"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_stay_separate_room",
                "utter_distance_clean_surfaces",
                "utter_wear_mask_same_room",
                "utter_self_isolation_link",
            ]
        )

    def test_fever_mild_symptoms_no_cough_no_contact(self):
        self._test_mild_symptoms_no_cough_no_contact(fever=True)

    def test_no_fever_mild_symptoms_no_cough_no_contact(self):
        self._test_mild_symptoms_no_cough_no_contact(fever=False)

    def _test_mild_symptoms_no_cough_no_contact(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.CONTACT,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.CONTACT, False),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.TRAVEL),
            ]
        )

        self.assert_templates(["utter_ask_travel"])

    def test_fever_mild_symptoms_no_cough_no_contact_travel(self):
        self._test_mild_symptoms_no_cough_no_contact_travel(fever=True)

    def test_no_fever_mild_symptoms_no_cough_no_contact_travel(self):
        self._test_mild_symptoms_no_cough_no_contact_travel(fever=False)

    def _test_mild_symptoms_no_cough_no_contact_travel(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.TRAVEL,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
                AssessmentSlots.CONTACT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.TRAVEL, True),
                SlotSet(REQUESTED_SLOT, AssessmentSlots.LIVES_ALONE),
            ]
        )

        self.assert_templates(
            ["utter_contact_risk_self_isolate", "utter_ask_lives_alone"]
        )

    def test_fever_mild_symptoms_no_cough_no_contact_travel_lives_alone(self):
        self._test_mild_symptoms_no_cough_no_contact_travel_lives_alone(fever=True)

    def test_no_fever_mild_symptoms_no_cough_no_contact_travel_lives_alone(self):
        self._test_mild_symptoms_no_cough_no_contact_travel_lives_alone(fever=False)

    def _test_mild_symptoms_no_cough_no_contact_travel_lives_alone(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
                AssessmentSlots.CONTACT: False,
                AssessmentSlots.TRAVEL: True,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.LIVES_ALONE, True),
                SlotSet(CONTACT_RISK_SLOT, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "none"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_dont_leave_home", "utter_self_isolation_link"])

    def test_fever_mild_symptoms_no_cough_no_contact_travel_not_lives_alone(self):
        self._test_mild_symptoms_no_cough_no_contact_travel_not_lives_alone(fever=True)

    def test_no_fever_mild_symptoms_no_cough_no_contact_travel_not_lives_alone(self):
        self._test_mild_symptoms_no_cough_no_contact_travel_not_lives_alone(fever=False)

    def _test_mild_symptoms_no_cough_no_contact_travel_not_lives_alone(
        self, fever: bool
    ):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
                AssessmentSlots.CONTACT: False,
                AssessmentSlots.TRAVEL: True,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.LIVES_ALONE, False),
                SlotSet(CONTACT_RISK_SLOT, True),
                SlotSet(AssessmentSlots.SYMPTOMS, "none"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_stay_separate_room",
                "utter_distance_clean_surfaces",
                "utter_wear_mask_same_room",
                "utter_self_isolation_link",
            ]
        )

    def test_fever_mild_symptoms_no_cough_no_contact_no_travel(self):
        self._test_mild_symptoms_no_cough_no_contact_no_travel(fever=True)

    def test_no_fever_mild_symptoms_no_cough_no_contact_no_travel(self):
        self._test_mild_symptoms_no_cough_no_contact_no_travel(fever=False)

    def _test_mild_symptoms_no_cough_no_contact_no_travel(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AssessmentSlots.TRAVEL,
                AssessmentSlots.SEVERE_SYMPTOMS: False,
                AssessmentSlots.PROVINCE: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AssessmentSlots.AGE_OVER_65: False,
                AssessmentSlots.HAS_FEVER: fever,
                AssessmentSlots.MODERATE_SYMPTOMS: False,
                AssessmentSlots.HAS_COUGH: False,
                AssessmentSlots.CONTACT: False,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(AssessmentSlots.TRAVEL, False),
                SlotSet(AssessmentSlots.SYMPTOMS, "none"),
                SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])
