from typing import List
from unittest.mock import patch

from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.daily_ci_keep_or_cancel_form import (
    FORM_NAME,
    DailyCiKeepOrCancelForm,
)
from covidflow.constants import (
    AGE_OVER_65_SLOT,
    CONTINUE_CI_SLOT,
    FEEL_WORSE_SLOT,
    PRECONDITIONS_SLOT,
    PROVINCE_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .form_test_helper import FormTestCase

DOMAIN = {
    "responses": {
        "provincial_info_link_qc": [{"text": "info link qc"}],
        "provincial_info_link_bc": [{"text": "info link bc"}],
    }
}

RECOMMENDATIONS_VULNERABLE__NOT_HAS_211 = [
    "utter_daily_ci__recommendations__more_information_vulnerable_population",
    "utter_daily_ci__recommendations__tomorrow_ci",
    "utter_daily_ci__recommendations__recommendation_1",
    "utter_daily_ci__recommendations__recommendation_2",
]

RECOMMENDATIONS_GENERAL__NOT_HAS_211 = [
    "utter_daily_ci__recommendations__more_information_general",
    "utter_daily_ci__recommendations__tomorrow_ci",
    "utter_daily_ci__recommendations__recommendation_1",
    "utter_daily_ci__recommendations__recommendation_2",
]

RECOMMENDATIONS_VULNERABLE__HAS_211_OTHER = [
    "utter_daily_ci__recommendations__more_information_vulnerable_population",
    "utter_daily_ci__recommendations__211_other_provinces",
    "utter_daily_ci__recommendations__tomorrow_ci",
    "utter_daily_ci__recommendations__recommendation_1",
    "utter_daily_ci__recommendations__recommendation_2",
]

RECOMMENDATIONS_GENERAL__HAS_211_OTHER = [
    "utter_daily_ci__recommendations__more_information_general",
    "utter_daily_ci__recommendations__211_other_provinces",
    "utter_daily_ci__recommendations__tomorrow_ci",
    "utter_daily_ci__recommendations__recommendation_1",
    "utter_daily_ci__recommendations__recommendation_2",
]


RECOMMENDATIONS_VULNERABLE__HAS_211_QC = [
    "utter_daily_ci__recommendations__more_information_vulnerable_population",
    "utter_daily_ci__recommendations__211_qc",
    "utter_daily_ci__recommendations__tomorrow_ci",
    "utter_daily_ci__recommendations__recommendation_1",
    "utter_daily_ci__recommendations__recommendation_2",
]

RECOMMENDATIONS_GENERAL__HAS_211_QC = [
    "utter_daily_ci__recommendations__more_information_general",
    "utter_daily_ci__recommendations__211_qc",
    "utter_daily_ci__recommendations__tomorrow_ci",
    "utter_daily_ci__recommendations__recommendation_1",
    "utter_daily_ci__recommendations__recommendation_2",
]


class TestDailyCiKeepOrCancelForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = DailyCiKeepOrCancelForm()

        self.patcher = patch(
            "covidflow.actions.daily_ci_keep_or_cancel_form.cancel_reminder"
        )
        self.mock_cancel_reminder = self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

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
                SYMPTOMS_SLOT: Symptoms.NONE,
                FEEL_WORSE_SLOT: feel_worse,
                PRECONDITIONS_SLOT: preconditions,
                AGE_OVER_65_SLOT: age_over_65,
            },
            active_loop=False,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, CONTINUE_CI_SLOT)]
        )

        self.assert_templates(
            [
                "utter_daily_ci__keep_or_cancel__no_symptoms_recommendation",
                "utter_ask_daily_ci__keep_or_cancel__continue_ci_no_symptoms",
            ]
        )

    def test_mild_symptoms__not_feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MILD,
            feel_worse=False,
            preconditions=False,
            age_over_65=False,
        )

    def test_mild_symptoms__not_feel_worse__preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MILD,
            feel_worse=False,
            preconditions=True,
            age_over_65=False,
        )

    def test_mild_symptoms__not_feel_worse__no_preconditions__age_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MILD,
            feel_worse=False,
            preconditions=False,
            age_over_65=True,
        )

    def test_mild_symptoms__feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=False,
            age_over_65=False,
        )

    def test_mild_symptoms__feel_worse__preconditions__age_not_over_65__not_has_211(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=True,
            age_over_65=False,
            province="nu",
            recommendations=RECOMMENDATIONS_VULNERABLE__NOT_HAS_211,
        )

    def test_mild_symptoms__feel_worse__preconditions__age_not_over_65__has_211_other(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=True,
            age_over_65=False,
            province="bc",
            recommendations=RECOMMENDATIONS_VULNERABLE__HAS_211_OTHER,
        )

    def test_mild_symptoms__feel_worse__preconditions__age_not_over_65__has_211_qc(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=True,
            age_over_65=False,
            province="qc",
            recommendations=RECOMMENDATIONS_VULNERABLE__HAS_211_QC,
        )

    def test_mild_symptoms__feel_worse__no_preconditions__age_over_65__not_has_211(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=False,
            age_over_65=True,
            province="nu",
            recommendations=RECOMMENDATIONS_VULNERABLE__NOT_HAS_211,
        )

    def test_mild_symptoms__feel_worse__no_preconditions__age_over_65__has_211_other(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=False,
            age_over_65=True,
            province="bc",
            recommendations=RECOMMENDATIONS_VULNERABLE__HAS_211_OTHER,
        )

    def test_mild_symptoms__feel_worse__no_preconditions__age_over_65__has_211_qc(self):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MILD,
            feel_worse=True,
            preconditions=False,
            age_over_65=True,
            province="qc",
            recommendations=RECOMMENDATIONS_VULNERABLE__HAS_211_QC,
        )

    def test_moderate_symptoms__not_feel_worse__no_preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MODERATE,
            feel_worse=False,
            preconditions=False,
            age_over_65=False,
        )

    def test_moderate_symptoms__not_feel_worse__preconditions__age_not_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MODERATE,
            feel_worse=False,
            preconditions=True,
            age_over_65=False,
        )

    def test_moderate_symptoms__not_feel_worse__no_preconditions__age_over_65(self):
        self._test_symptoms_optional_ci(
            symptoms=Symptoms.MODERATE,
            feel_worse=False,
            preconditions=False,
            age_over_65=True,
        )

    def test_moderate_symptoms__feel_worse__no_preconditions__age_not_over_65__not_has_211(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MODERATE,
            feel_worse=True,
            preconditions=False,
            age_over_65=False,
            province="nu",
            recommendations=RECOMMENDATIONS_GENERAL__NOT_HAS_211,
        )

    def test_moderate_symptoms__feel_worse__no_preconditions__age_not_over_65__has_211_other(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MODERATE,
            feel_worse=True,
            preconditions=False,
            age_over_65=False,
            province="bc",
            recommendations=RECOMMENDATIONS_GENERAL__HAS_211_OTHER,
        )

    def test_moderate_symptoms__feel_worse__no_preconditions__age_not_over_65__has_211_qc(
        self,
    ):
        self._test_symptoms_mandatory_ci(
            symptoms=Symptoms.MODERATE,
            feel_worse=True,
            preconditions=False,
            age_over_65=False,
            province="qc",
            recommendations=RECOMMENDATIONS_GENERAL__HAS_211_QC,
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
            active_loop=False,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, CONTINUE_CI_SLOT)]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__keep_or_cancel__continue_ci_symptoms"]
        )

    def _test_symptoms_mandatory_ci(
        self,
        symptoms: str,
        feel_worse: bool,
        preconditions: bool,
        age_over_65: bool,
        province: bool,
        recommendations: List[str],
    ):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: age_over_65,
                FEEL_WORSE_SLOT: feel_worse,
                PRECONDITIONS_SLOT: preconditions,
                SYMPTOMS_SLOT: symptoms,
                PROVINCE_SLOT: province,
            },
            active_loop=False,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(
            [
                "utter_daily_ci__keep_or_cancel__feel_worse_keep_ci",
                "utter_daily_ci__keep_or_cancel__feel_worse_recommendation",
            ]
            + recommendations
        )

    def test_no_symptoms_ci_continue(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CONTINUE_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.NONE,
            },
            intent="continue",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(CONTINUE_CI_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__keep_or_cancel__acknowledge_continue_ci"]
        )

        self.mock_cancel_reminder.assert_not_called()

    def test_symptoms_ci_continue__not_has_211(self):
        self._test_symptoms_ci_continue(
            province="nu", recommendations=RECOMMENDATIONS_GENERAL__NOT_HAS_211
        )

    def test_symptoms_ci_continue__has_211_other(self):
        self._test_symptoms_ci_continue(
            province="bc", recommendations=RECOMMENDATIONS_GENERAL__HAS_211_OTHER
        )

    def test_symptoms_ci_continue__has_211_qc(self):
        self._test_symptoms_ci_continue(
            province="qc", recommendations=RECOMMENDATIONS_GENERAL__HAS_211_QC
        )

    def _test_symptoms_ci_continue(self, province: str, recommendations: List[str]):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CONTINUE_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
                PROVINCE_SLOT: province,
            },
            intent="continue",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(CONTINUE_CI_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_daily_ci__keep_or_cancel__acknowledge_continue_ci"]
            + recommendations
        )

        self.mock_cancel_reminder.assert_not_called()

    def test_no_symptoms_ci_cancel(self):
        self._test_ci_cancel(symptoms=Symptoms.NONE)

    def test_symptoms_ci_cancel(self):
        self._test_ci_cancel(symptoms=Symptoms.MILD)

    def _test_ci_cancel(self, symptoms: str):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CONTINUE_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: symptoms,
            },
            intent="cancel",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(CONTINUE_CI_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_daily_ci__keep_or_cancel__acknowledge_cancel_ci",
                "utter_daily_ci__keep_or_cancel__cancel_ci_recommendation",
            ]
        )

        self.mock_cancel_reminder.assert_called()

    def test_symptoms_ask_continue_ci_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CONTINUE_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.MILD,
            },
            intent="anything_else",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(CONTINUE_CI_SLOT, None), SlotSet(REQUESTED_SLOT, CONTINUE_CI_SLOT)]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__keep_or_cancel__continue_ci_symptoms_error"]
        )

    def test_no_symptoms_ask_continue_ci_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: CONTINUE_CI_SLOT,
                AGE_OVER_65_SLOT: False,
                FEEL_WORSE_SLOT: False,
                PRECONDITIONS_SLOT: False,
                SYMPTOMS_SLOT: Symptoms.NONE,
            },
            intent="anything_else",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(CONTINUE_CI_SLOT, None), SlotSet(REQUESTED_SLOT, CONTINUE_CI_SLOT)]
        )

        self.assert_templates(
            ["utter_ask_daily_ci__keep_or_cancel__continue_ci_no_symptoms_error"]
        )
