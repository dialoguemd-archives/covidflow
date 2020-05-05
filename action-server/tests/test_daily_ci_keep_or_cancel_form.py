from rasa_sdk.events import FollowupAction, Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from actions.action_daily_ci_recommendations import (
    ACTION_NAME as RECOMMENDATIONS_ACTION_NAME,
)
from actions.daily_ci_keep_or_cancel_form import (
    AGE_OVER_65_SLOT,
    CANCEL_CI_SLOT,
    FEEL_WORSE_SLOT,
    FORM_NAME,
    PRECONDITIONS_SLOT,
    SYMPTOMS_SLOT,
    DailyCiKeepOrCancelForm,
)
from tests.form_helper import FormTestCase


class TestDailyCiKeepOrCancelForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiKeepOrCancelForm()

    def test_no_symptoms__not_feel_worse__no_preconditions__age_not_over_65(self):
        self._test_no_symptoms(feel_worse=False, preconditions=False, age_over_65=False)

    def test_no_symptoms__not_feel_worse__no_preconditions__age_over_65(self):
        self._test_no_symptoms(feel_worse=False, preconditions=False, age_over_65=True)

    def test_no_symptoms__not_feel_worse__preconditions__age_not_over_65(self):
        self._test_no_symptoms(feel_worse=False, preconditions=True, age_over_65=False)

    def test_no_symptoms__feel_worse__no_preconditions__age_not_over_65(self):
        self._test_no_symptoms(feel_worse=True, preconditions=False, age_over_65=False)

    def _test_no_symptoms(
        self, feel_worse: bool, preconditions: bool, age_over_65: bool
    ):
        tracker = self.create_tracker(
            slots={
                SYMPTOMS_SLOT: "none",
                FEEL_WORSE_SLOT: feel_worse,
                PRECONDITIONS_SLOT: preconditions,
                AGE_OVER_65_SLOT: age_over_65,
            },
            active_form=False,
        )

        self.run_form(tracker)

        self.assert_events([Form(FORM_NAME), SlotSet(REQUESTED_SLOT, CANCEL_CI_SLOT)])

        self.assert_templates(
            [
                "utter_daily_ci__keep_or_cancel__no_symptoms_recommendation",
                "utter_ask_daily_ci__keep_or_cancel__cancel_ci_no_symptoms",
            ]
        )

    def test_mild_symptoms__not_feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="mild", feel_worse=False, preconditions=False, age_over_65=False
        )

    def test_mild_symptoms__not_feel_worse__preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="mild", feel_worse=False, preconditions=True, age_over_65=False
        )

    def test_mild_symptoms__not_feel_worse__no_preconditions__age_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="mild", feel_worse=False, preconditions=False, age_over_65=True
        )

    def test_mild_symptoms__feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="mild", feel_worse=True, preconditions=False, age_over_65=False
        )

    def test_mild_symptoms__feel_worse__preconditions__age_not_over_65(self):
        self._test_symptoms_mandatory_ci(
            symptoms="mild", feel_worse=True, preconditions=True, age_over_65=False
        )

    def test_mild_symptoms__feel_worse__no_preconditions__age_over_65(self):
        self._test_symptoms_mandatory_ci(
            symptoms="mild", feel_worse=True, preconditions=False, age_over_65=True
        )

    def test_moderate_symptoms__not_feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="moderate",
            feel_worse=False,
            preconditions=False,
            age_over_65=False,
        )

    def test_moderate_symptoms__not_feel_worse__preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="moderate",
            feel_worse=False,
            preconditions=True,
            age_over_65=False,
        )

    def test_moderate_symptoms__not_feel_worse__no_preconditions__age_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms="moderate",
            feel_worse=False,
            preconditions=False,
            age_over_65=True,
        )

    def test_moderate_symptoms__feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_mandatory_ci(
            symptoms="moderate",
            feel_worse=True,
            preconditions=False,
            age_over_65=False,
        )

    def _test_symptoms_optional_ci(
        self, symptoms: str, feel_worse: bool, preconditions: bool, age_over_65: bool
    ):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: age_over_65,
                FEEL_WORSE_SLOT: feel_worse,
                PRECONDITIONS_SLOT: preconditions,
                SYMPTOMS_SLOT: symptoms,
            },
            active_form=False,
        )

        self.run_form(tracker)

        self.assert_events([Form(FORM_NAME), SlotSet(REQUESTED_SLOT, CANCEL_CI_SLOT)])

        self.assert_templates(
            ["utter_ask_daily_ci__keep_or_cancel__cancel_ci_symptoms"]
        )

    def _test_symptoms_mandatory_ci(
        self, symptoms: str, feel_worse: bool, preconditions: bool, age_over_65: bool
    ):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: age_over_65,
                FEEL_WORSE_SLOT: feel_worse,
                PRECONDITIONS_SLOT: preconditions,
                SYMPTOMS_SLOT: symptoms,
            },
            active_form=False,
        )

        self.run_form(tracker)

        self.assert_events(
            [
                Form(FORM_NAME),
                FollowupAction(RECOMMENDATIONS_ACTION_NAME),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__keep_or_cancel__feel_worse_keep_ci",
                "utter_daily_ci__keep_or_cancel__feel_worse_recommendation",
            ]
        )

    def test_no_symptoms_ci_continue(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CANCEL_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: "none",
            },
            intent="continue",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(CANCEL_CI_SLOT, False), Form(None), SlotSet(REQUESTED_SLOT, None)]
        )

        self.assert_templates(
            ["utter_daily_ci__keep_or_cancel__acknowledge_continue_ci"]
        )

    def test_symptoms_ci_continue(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CANCEL_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: "mild",
            },
            intent="continue",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(CANCEL_CI_SLOT, False),
                FollowupAction(RECOMMENDATIONS_ACTION_NAME),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__keep_or_cancel__acknowledge_continue_ci"]
        )

    def test_no_symptoms_ci_cancel(self):
        self._test_ci_cancel(symptoms="none")

    def test_symptoms_ci_cancel(self):
        self._test_ci_cancel(symptoms="mild")

    def _test_ci_cancel(self, symptoms: str):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CANCEL_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: symptoms,
            },
            intent="cancel",
        )

        self.run_form(tracker)

        self.assert_events(
            [SlotSet(CANCEL_CI_SLOT, True), Form(None), SlotSet(REQUESTED_SLOT, None)]
        )

        self.assert_templates(
            [
                "utter_daily_ci__keep_or_cancel__acknowledge_cancel_ci",
                "utter_daily_ci__keep_or_cancel__cancel_ci_recommendation",
            ]
        )
