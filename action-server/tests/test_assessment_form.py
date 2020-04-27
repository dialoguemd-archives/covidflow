from rasa_sdk.events import Form, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from actions.assessment_form import AssessmentForm
from tests.form_helper import FormTestCase


class BaseTestAssessmentForm:
    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False, intent=self.assessment_type)

        self.run_form(tracker)

        self.assert_events(
            [
                Form("assessment_form"),
                SlotSet("assessment_type", self.assessment_type),
                SlotSet(REQUESTED_SLOT, "severe_symptoms"),
            ],
        )

        self.assert_templates(["utter_ask_severe_symptoms"])

    def test_provide_severe_symptoms_affirm(self):
        tracker = self.create_tracker(
            slots={
                "assessment_type": self.assessment_type,
                REQUESTED_SLOT: "severe_symptoms",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet("severe_symptoms", True),
                SlotSet("symptoms", "severe"),
                SlotSet("self_assess_done", True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])

    def test_provide_severe_symptoms_deny(self):
        tracker = self.create_tracker(
            slots={
                "assessment_type": self.assessment_type,
                REQUESTED_SLOT: "severe_symptoms",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("severe_symptoms", False), SlotSet(REQUESTED_SLOT, "province"),],
        )

        self.assert_templates(["utter_ask_province"])

    def test_provide_province(self):
        tracker = self.create_tracker(
            slots={
                "assessment_type": self.assessment_type,
                "severe_symptoms": False,
                REQUESTED_SLOT: "province",
            },
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                "assessment_type": self.assessment_type,
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
                SlotSet("symptoms", "none"),
                SlotSet("self_assess_done", True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ],
        )

        self.assert_templates([])


class TestAssessmentFormTestedPositive(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = AssessmentForm()
        self.dispatcher = CollectingDispatcher()
        self.assessment_type = "tested_positive"

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False, intent=self.assessment_type)

        self.run_form(tracker)

        self.assert_events(
            [
                Form("assessment_form"),
                SlotSet("assessment_type", self.assessment_type),
                SlotSet(REQUESTED_SLOT, "severe_symptoms"),
            ],
        )

        self.assert_templates(
            [
                "utter_self_isolate_separate_room",
                "utter_dont_leave_home",
                "utter_deliver_food_medications",
                "utter_home_assistance",
                "utter_assess_symptoms",
                "utter_ask_severe_symptoms",
            ],
        )


class TestAssessmentFormSuspect(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = AssessmentForm()
        self.dispatcher = CollectingDispatcher()
        self.assessment_type = "suspect"


class TestAssessmentFormGetAssessment(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = AssessmentForm()
        self.dispatcher = CollectingDispatcher()
        self.assessment_type = "suspect"

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False, intent="get_assessment")

        self.run_form(tracker)

        self.assert_events(
            [
                Form("assessment_form"),
                SlotSet("assessment_type", "suspect"),
                SlotSet(REQUESTED_SLOT, "severe_symptoms"),
            ],
        )

        self.assert_templates(["utter_ask_severe_symptoms"])


class TestAssessmentFormCheckinReturn(BaseTestAssessmentForm, FormTestCase):
    def setUp(self):
        self.form = AssessmentForm()
        self.dispatcher = CollectingDispatcher()
        self.assessment_type = "checkin_return"

    def test_form_activation(self):
        tracker = self.create_tracker(active_form=False, intent=self.assessment_type)

        self.run_form(tracker)

        self.assert_events(
            [
                Form("assessment_form"),
                SlotSet("assessment_type", self.assessment_type),
                SlotSet(REQUESTED_SLOT, "severe_symptoms"),
            ],
        )

        self.assert_templates(
            ["utter_returning_for_checkin", "utter_ask_severe_symptoms"]
        )

    def test_provide_has_fever_affirm(self):
        tracker = self.create_tracker(
            slots={
                "assessment_type": self.assessment_type,
                "severe_symptoms": False,
                "province": "qc",
                "age_over_65": False,
                REQUESTED_SLOT: "has_fever",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet("has_fever", True), SlotSet(REQUESTED_SLOT, "moderate_symptoms")],
        )

        self.assert_templates(
            [
                "utter_self_isolate_reminder",
                "utter_home_assistance",
                "utter_ask_moderate_symptoms",
            ],
        )

    def test_provide_has_fever_deny(self):
        tracker = self.create_tracker(
            slots={
                "assessment_type": self.assessment_type,
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

        self.assert_templates(
            [
                "utter_self_isolate_reminder",
                "utter_home_assistance",
                "utter_ask_moderate_symptoms",
            ],
        )
