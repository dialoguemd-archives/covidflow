from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.tested_positive_form import (
    FORM_NAME,
    MILD_SYMPTOMS_WORSENED_SLOT,
    TestedPositiveForm,
)
from covidflow.constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    LIVES_ALONE_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
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
        "utter_ask_lives_alone_error": [{"text": ""}],
        "utter_ask_severe_symptoms_error": [{"text": ""}],
        "utter_ask_age_over_65_error": [{"text": ""}],
        "utter_ask_has_fever_error": [{"text": ""}],
        "utter_ask_moderate_symptoms_error": [{"text": ""}],
        "utter_ask_tested_positive__mild_symptoms_worsened_error": [{"text": ""}],
        "utter_ask_has_cough_error": [{"text": ""}],
        "utter_ask_province_code_error": [{"text": ""}],
    }
}


class TestTestedPositiveForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = TestedPositiveForm()

    def test_form_activation(self):
        tracker = self.create_tracker(active_loop=False)

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, LIVES_ALONE_SLOT)]
        )

        self.assert_templates(
            [
                "utter_tested_positive_entry",
                "utter_tested_positive_self_isolate",
                "utter_ask_lives_alone",
            ]
        )

    def test_lives_alone(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: LIVES_ALONE_SLOT}, intent="affirm"
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(LIVES_ALONE_SLOT, True),
                SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_dont_leave_home",
                "utter_self_isolation_link",
                "utter_assess_symptoms",
                "utter_ask_severe_symptoms",
            ]
        )

    def test_not_lives_alone(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: LIVES_ALONE_SLOT}, intent="deny"
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(LIVES_ALONE_SLOT, False),
                SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_stay_separate_room",
                "utter_distance_clean_surfaces",
                "utter_wear_mask_same_room",
                "utter_self_isolation_link",
                "utter_assess_symptoms",
                "utter_ask_severe_symptoms",
            ]
        )

    def test_lives_alone_error(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: LIVES_ALONE_SLOT}, text="anything"
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(LIVES_ALONE_SLOT, None),
                SlotSet(REQUESTED_SLOT, LIVES_ALONE_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_lives_alone_error"])

    def test_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT, LIVES_ALONE_SLOT: False,},
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.SEVERE),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_not_severe_symptoms(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT, LIVES_ALONE_SLOT: False,},
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, PROVINCE_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_pre_ask_province_code", "utter_ask_province_code"]
        )

    def test_severe_symptoms_error(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: SEVERE_SYMPTOMS_SLOT, LIVES_ALONE_SLOT: False,},
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(SEVERE_SYMPTOMS_SLOT, None),
                SlotSet(REQUESTED_SLOT, SEVERE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_severe_symptoms_error"])

    def test_collect_province(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: PROVINCE_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
            },
            intent="inform",
            entities=[{"entity": "province", "value": "qc"}],
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(PROVINCE_SLOT, "qc"),
                SlotSet(PROVINCIAL_811_SLOT, "811 qc"),
                SlotSet(REQUESTED_SLOT, AGE_OVER_65_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_age_over_65"])

    def test_collect_province_error(self):
        tracker = self.create_tracker(
            slots={
                SEVERE_SYMPTOMS_SLOT: False,
                LIVES_ALONE_SLOT: False,
                REQUESTED_SLOT: PROVINCE_SLOT,
            },
            intent="inform",
            entities=[{"entity": "province", "value": "ae"}],
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(PROVINCE_SLOT, None), SlotSet(REQUESTED_SLOT, PROVINCE_SLOT),],
        )

        self.assert_templates(["utter_ask_province_code_error"])

    def test_collect_age_over_65(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AGE_OVER_65_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(AGE_OVER_65_SLOT, True), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),]
        )

        self.assert_templates(["utter_ask_has_fever"])

    def test_collect_age_over_65_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: AGE_OVER_65_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(AGE_OVER_65_SLOT, None),
                SlotSet(REQUESTED_SLOT, AGE_OVER_65_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_age_over_65_error"])

    def test_fever(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_FEVER_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

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
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_FEVER_SLOT, False),
                SlotSet(REQUESTED_SLOT, MODERATE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_moderate_symptoms"])

    def test_fever_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_FEVER_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_FEVER_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_FEVER_SLOT),]
        )

        self.assert_templates(["utter_ask_has_fever_error"])

    def test_fever_moderate_symptoms(self):
        self._test_moderate_symptoms(fever=True)

    def test_no_fever_moderate_symptoms(self):
        self._test_moderate_symptoms(fever=False)

    def _test_moderate_symptoms(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
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
            ]
        )

        self.assert_templates(["utter_symptoms_worsen_emergency_assistance"])

    def test_fever_mild_symptoms(self):
        self._test_mild_symptoms(fever=True)

    def test_no_fever_mild_symptoms(self):
        self._test_mild_symptoms(fever=False)

    def _test_mild_symptoms(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MODERATE_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),
            ]
        )

        self.assert_templates(["utter_moderate_symptoms_false", "utter_ask_has_cough"])

    def test_moderate_symptoms_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MODERATE_SYMPTOMS_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MODERATE_SYMPTOMS_SLOT, None),
                SlotSet(REQUESTED_SLOT, MODERATE_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_moderate_symptoms_error"])

    def test_fever_mild_symptoms_cough(self):
        self._test_mild_symptoms_cough(fever=True)

    def test_no_fever_mild_symptoms_cough(self):
        self._test_mild_symptoms_cough(fever=False)

    def _test_mild_symptoms_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, True),
                SlotSet(REQUESTED_SLOT, MILD_SYMPTOMS_WORSENED_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_tested_positive__mild_symptoms_worsened"])

    def test_fever_mild_symptoms_no_cough(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(REQUESTED_SLOT, MILD_SYMPTOMS_WORSENED_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_tested_positive__mild_symptoms_worsened"])

    def test_cough_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(HAS_COUGH_SLOT, None), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT),]
        )

        self.assert_templates(["utter_ask_has_cough_error"])

    def test_no_symptoms(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                MODERATE_SYMPTOMS_SLOT: False,
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
            ]
        )

        self.assert_templates([])

    def test_mild_symptoms_worse_cough_fever(self):
        self._test_mild_symptoms_worse(fever=True, cough=True)

    def test_mild_symptoms_worse_cough_no_fever(self):
        self._test_mild_symptoms_worse(fever=False, cough=True)

    def test_mild_symptoms_worse_no_cough_fever(self):
        self._test_mild_symptoms_worse(fever=True, cough=False)

    def _test_mild_symptoms_worse(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MILD_SYMPTOMS_WORSENED_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MILD_SYMPTOMS_WORSENED_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_symptoms_worsen_emergency_assistance"])

    def test_mild_symptoms_not_worse_cough_fever(self):
        self._test_mild_symptoms_not_worse(fever=True, cough=True)

    def test_mild_symptoms_not_worse_cough_no_fever(self):
        self._test_mild_symptoms_not_worse(fever=False, cough=True)

    def test_mild_symptoms_not_worse_no_cough_fever(self):
        self._test_mild_symptoms_not_worse(fever=True, cough=False)

    def _test_mild_symptoms_not_worse(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MILD_SYMPTOMS_WORSENED_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MILD_SYMPTOMS_WORSENED_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, Symptoms.MILD),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_mild_symptoms_worsened_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: MILD_SYMPTOMS_WORSENED_SLOT,
                LIVES_ALONE_SLOT: False,
                SEVERE_SYMPTOMS_SLOT: False,
                PROVINCE_SLOT: "qc",
                PROVINCIAL_811_SLOT: "811 qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: True,
                HAS_COUGH_SLOT: True,
                MODERATE_SYMPTOMS_SLOT: False,
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(MILD_SYMPTOMS_WORSENED_SLOT, None),
                SlotSet(REQUESTED_SLOT, MILD_SYMPTOMS_WORSENED_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_ask_tested_positive__mild_symptoms_worsened_error"]
        )
