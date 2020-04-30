from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import Form, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

from actions.assessment_common import AssessmentCommon
from tests.form_helper import FormTestCase


class TestAssessmentForm(FormAction):
    def name(self) -> Text:

        return "test_assessment_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return AssessmentCommon.base_required_slots(tracker)

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return AssessmentCommon.slot_mappings(self)

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
            slots={REQUESTED_SLOT: "severe_symptoms",}, intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("severe_symptoms", True),
                SlotSet("risk_level", "common"),
                SlotSet("symptoms", "severe"),
                SlotSet("self_assess_done", True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_severe_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: "severe_symptoms",}, intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("severe_symptoms", False), SlotSet(REQUESTED_SLOT, "province"),],
        )

        self.assert_templates(["utter_ask_province"])

    def test_provide_province(self):
        tracker = self.create_tracker(
            slots={"severe_symptoms": False, REQUESTED_SLOT: "province",},
            intent="inform",
            entities=[{"entity": "province", "value": "qc"}],
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("province", "qc"), SlotSet(REQUESTED_SLOT, "age_over_65"),],
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_provide_age_over_65_affirm(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                REQUESTED_SLOT: "age_over_65",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("age_over_65", True), SlotSet(REQUESTED_SLOT, "has_fever"),],
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_provide_age_over_65_deny(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                REQUESTED_SLOT: "age_over_65",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("age_over_65", False), SlotSet(REQUESTED_SLOT, "has_fever"),],
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_provide_has_fever_affirm(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                REQUESTED_SLOT: "has_fever",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("has_fever", True), SlotSet(REQUESTED_SLOT, "moderate_symptoms"),],
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_provide_has_fever_deny(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                REQUESTED_SLOT: "has_fever",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("has_fever", False),
                SlotSet(REQUESTED_SLOT, "moderate_symptoms"),
            ],
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_provide_moderate_symptoms_affirm(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                "has_fever": False,
                REQUESTED_SLOT: "moderate_symptoms",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("moderate_symptoms", True),
                SlotSet("risk_level", "elevated-medical-risk"),
                SlotSet("symptoms", "moderate"),
                SlotSet("self_assess_done", True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_moderate_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                "has_fever": False,
                REQUESTED_SLOT: "moderate_symptoms",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("moderate_symptoms", False),
                SlotSet(REQUESTED_SLOT, "has_cough"),
            ],
        )

        self.assert_templates(["utter_ask_has_cough"])

    def test_provide_has_cough_affirm(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                "has_fever": False,
                "moderate_symptoms": False,
                REQUESTED_SLOT: "has_cough",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("has_cough", True),
                SlotSet("risk_level", "common"),
                SlotSet("symptoms", "mild"),
                SlotSet("self_assess_done", True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_has_cough_deny(self):
        tracker = self.create_tracker(
            slots={
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                "has_fever": False,
                "moderate_symptoms": False,
                REQUESTED_SLOT: "has_cough",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("has_cough", False),
                SlotSet("risk_level", "common"),
                SlotSet("symptoms", "none"),
                SlotSet("self_assess_done", True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

        def test_risk_level_no_symptoms_no_risk(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": False,
                    "has_fever": False,
                    "moderate_symptoms": False,
                    "has_cough": False,
                },
            )

            self.assertIn(
                SlotSet("risk_level", "common"),
                self.submit(tracker, self.dispatcher, {}),
            )

        def test_risk_level_over_65(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": True,
                    "has_fever": False,
                    "moderate_symptoms": False,
                    "has_cough": False,
                },
            )

            self.assertIn(
                SlotSet("risk_level", "elevated-medical-risk"),
                self.submit(tracker, self.dispatcher, {}),
            )

        def test_risk_level_moderate_symptoms(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": False,
                    "has_fever": False,
                    "moderate_symptoms": True,
                },
            )

            assert self.submit(tracker, self.dispatcher, {}) == [
                SlotSet("risk_level", "elevated-medical-risk")
            ]

        def test_risk_level_mild_symptoms(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": False,
                    "has_fever": False,
                    "moderate_symptoms": False,
                    "has_cough": True,
                },
            )

            self.assertIn(
                SlotSet("risk_level", "common"),
                self.submit(tracker, self.dispatcher, {}),
            )

        def test_risk_level_travel_risk(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": False,
                    "has_fever": False,
                    "moderate_symptoms": False,
                    "has_cough": False,
                    "travel": True,
                },
            )

            self.assertIn(
                SlotSet("risk_level", "elevated-covid-risk"),
                self.submit(tracker, self.dispatcher, {}),
            )

        def test_risk_level_contact_risk(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": False,
                    "has_fever": False,
                    "moderate_symptoms": False,
                    "has_cough": False,
                    "contact": True,
                },
            )

            self.assertIn(
                SlotSet("risk_level", "elevated-covid-risk"),
                self.submit(tracker, self.dispatcher, {}),
            )

        def test_risk_level_medical_and_covid_risk(self):
            tracker = self.create_tracker(
                slots={
                    "severe_symptoms": False,
                    "province": "qc",
                    "age_over_65": True,
                    "has_fever": False,
                    "moderate_symptoms": False,
                    "has_cough": False,
                    "travel": True,
                },
            )

            self.assertIn(
                SlotSet("risk_level", "elevated-medical-risk,elevated-covid-risk"),
                self.submit(tracker, self.dispatcher, {}),
            )


class TestAssessmentFormSuspect(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = TestAssessmentForm()
        self.dispatcher = CollectingDispatcher()
