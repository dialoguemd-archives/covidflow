from rasa_sdk.events import Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from actions.daily_ci_feel_better_form import (
    FEEL_WORSE_SLOT,
    FORM_NAME,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    HAS_OTHER_MILD_SYMPTOMS_SLOT,
    IS_SYMPTOM_FREE_SLOT,
    LAST_SYMPTOMS_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SYMPTOMS_SLOT,
    DailyCiFeelBetterForm,
)
from tests.form_helper import FormTestCase


class TestDailyCiFeelBetterForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiFeelBetterForm()

    def test_moderate(self):
        self._test_form_activation(last_symptoms="moderate")

    def test_mild(self):
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

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__acknowledge",
                "utter_ask_daily_ci__feel_better__has_fever",
            ]
        )

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
            [SlotSet(HAS_FEVER_SLOT, True), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT)]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_fever",
                "utter_daily_ci__take_acetaminophen",
                "utter_daily_ci__avoid_ibuprofen",
                "utter_ask_daily_ci__feel_better__has_cough",
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
            [SlotSet(HAS_FEVER_SLOT, False), SlotSet(REQUESTED_SLOT, HAS_COUGH_SLOT)]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__acknowledge_no_fever",
                "utter_ask_daily_ci__feel_better__has_cough",
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
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
                "utter_ask_daily_ci__feel_better__has_diff_breathing",
            ]
        )

    def test_moderate_last_symptoms__fever_no_cough(self):
        self._test_moderate_last_symptoms__no_cough(fever=True)

    def test_moderate_last_symptoms__no_fever_no_cough(self):
        self._test_moderate_last_symptoms__no_cough(fever=False)

    def _test_moderate_last_symptoms__no_cough(self, fever: bool):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: HAS_COUGH_SLOT,
                LAST_SYMPTOMS_SLOT: "moderate",
                HAS_FEVER_SLOT: fever,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_COUGH_SLOT, False),
                SlotSet(REQUESTED_SLOT, HAS_DIFF_BREATHING_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_ask_daily_ci__feel_better__has_diff_breathing",
            ]
        )

    def test_moderate_last_symptoms__fever_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__diff_breathing(self):
        self._test_moderate_last_symptoms__diff_breathing(fever=False, cough=False)

    def _test_moderate_last_symptoms__diff_breathing(self, fever: bool, cough: bool):
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
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__breathing_difficulty_recommendation_1",
                "utter_daily_ci__feel_better__breathing_difficulty_recommendation_2",
            ]
        )

    def test_moderate_last_symptoms__fever_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__no_diff_breathing(self):
        self._test_moderate_last_symptoms__no_diff_breathing(fever=False, cough=False)

    def _test_moderate_last_symptoms__no_diff_breathing(self, fever: bool, cough: bool):
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

        self.assert_events(
            [
                SlotSet(HAS_DIFF_BREATHING_SLOT, False),
                SlotSet(SYMPTOMS_SLOT, "mild"),
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_ask_daily_ci__feel_better__has_other_mild_symptoms_with_acknowledge"
            ]
        )

    def test_moderate_last_symptoms__fever_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=True, cough=False)

    def test_moderate_last_symptoms__no_fever_no_cough__other_mild(self):
        self._test_moderate_last_symptoms__mild(fever=False, cough=False)

    def _test_moderate_last_symptoms__mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: "mild",
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

    def test_moderate_last_symptoms__fever_cough__no_other_mild(self):
        self._test_moderate_last_symptoms__no_other_mild(fever=True, cough=True)

    def test_moderate_last_symptoms__no_fever_cough__no_other_mild(self):
        self._test_moderate_last_symptoms__no_other_mild(fever=False, cough=True)

    def test_moderate_last_symptoms__fever_no_cough__no_other_mild(self):
        self._test_moderate_last_symptoms__no_other_mild(fever=True, cough=False)

    def _test_moderate_last_symptoms__no_other_mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: "mild",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

    def test_moderate_last_symptoms__no_fever_no_cough__no_other_mild(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                SYMPTOMS_SLOT: "mild",
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, False),
                SlotSet(REQUESTED_SLOT, IS_SYMPTOM_FREE_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_daily_ci__feel_better__is_symptom_free"])

    def test_moderate_last_symptoms__symptom_free(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
                SYMPTOMS_SLOT: "mild",
            },
            intent="symptom_free",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, "none"),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_moderate_last_symptoms__still_sick(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "moderate",
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_DIFF_BREATHING_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
                SYMPTOMS_SLOT: "mild",
            },
            intent="still_sick",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__has_other_mild_symptoms_still_sick_recommendation"
            ]
        )

    def test_mild_last_symptoms__fever_cough(self):
        self._test_other_mild_last_symptoms__cough(fever=True)

    def test_mild_last_symptoms__no_fever_cough(self):
        self._test_other_mild_last_symptoms__cough(fever=False)

    def _test_other_mild_last_symptoms__cough(self, fever: bool):
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
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__cough_syrup_may_help",
                "utter_daily_ci__cough_syrup_pharmacist",
                "utter_ask_daily_ci__feel_better__has_other_mild_symptoms",
            ]
        )

    def test_mild_last_symptoms__fever_no_cough(self):
        self._test_other_mild_last_symptoms__no_cough(fever=True)

    def test_mild_last_symptoms__no_fever_no_cough(self):
        self._test_other_mild_last_symptoms__no_cough(fever=False)

    def _test_other_mild_last_symptoms__no_cough(self, fever: bool):
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
                SlotSet(REQUESTED_SLOT, HAS_OTHER_MILD_SYMPTOMS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__acknowledge_no_cough",
                "utter_ask_daily_ci__feel_better__has_other_mild_symptoms",
            ]
        )

    def test_mild_last_symptoms__fever_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=True, cough=True)

    def test_mild_last_symptoms__no_fever_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=False, cough=True)

    def test_mild_last_symptoms__fever_no_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=True, cough=False)

    def test_mild_last_symptoms__no_fever_no_cough__other_mild(self):
        self._test_mild_last_symptoms__other_mild(fever=False, cough=False)

    def _test_mild_last_symptoms__other_mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "mild",
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, True),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

    def test_mild_last_symptoms__fever_cough__no_other_mild(self):
        self._test_mild_last_symptoms__no_other_mild(fever=True, cough=True)

    def test_mild_last_symptoms__no_fever_cough__no_other_mild(self):
        self._test_mild_last_symptoms__no_other_mild(fever=False, cough=True)

    def test_mild_last_symptoms__fever_no_cough__no_other_mild(self):
        self._test_mild_last_symptoms__no_other_mild(fever=True, cough=False)

    def _test_mild_last_symptoms__no_other_mild(self, fever: bool, cough: bool):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "mild",
                REQUESTED_SLOT: HAS_OTHER_MILD_SYMPTOMS_SLOT,
                HAS_FEVER_SLOT: fever,
                HAS_COUGH_SLOT: cough,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"]
        )

    def test_mild_last_symptoms__symptom_free(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "mild",
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
            },
            intent="symptom_free",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, True),
                SlotSet(SYMPTOMS_SLOT, "none"),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_mild_last_symptoms__still_sick(self):
        tracker = self.create_tracker(
            slots={
                LAST_SYMPTOMS_SLOT: "mild",
                REQUESTED_SLOT: IS_SYMPTOM_FREE_SLOT,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                HAS_OTHER_MILD_SYMPTOMS_SLOT: False,
            },
            intent="still_sick",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(IS_SYMPTOM_FREE_SLOT, False),
                SlotSet(SELF_ASSESS_DONE_SLOT, True),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__feel_better__has_other_mild_symptoms_still_sick_recommendation"
            ]
        )
