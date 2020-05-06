from rasa_sdk.events import FollowupAction

from actions.action_daily_ci_recommendations import (
    AGE_OVER_65_SLOT,
    PRECONDITIONS_SLOT,
    PROVINCE_SLOT,
    ActionDailyCiRecommendations,
)
from actions.action_goodbye import ACTION_NAME as GOODBYE_ACTION_NAME
from tests.action_helper import ActionTestCase


class ActionDailyCiRecommendationsTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionDailyCiRecommendations()

    def test_age_over_65__no_preconditions__not_has_211(self):
        self._test_vulnerable_population__not_has_211(
            age_over_65=True, preconditions=False
        )

    def test_age_over_65__preconditions__not_has_211(self):
        self._test_vulnerable_population__not_has_211(
            age_over_65=True, preconditions=True
        )

    def test_not_age_over_65__preconditions__not_has_211(self):
        self._test_vulnerable_population__not_has_211(
            age_over_65=False, preconditions=True
        )

    def _test_vulnerable_population__not_has_211(
        self, age_over_65: bool, preconditions: bool
    ):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: age_over_65,
                PRECONDITIONS_SLOT: preconditions,
                PROVINCE_SLOT: "xyz",
            },
        )

        self.run_action(tracker)

        self.assert_events([FollowupAction(GOODBYE_ACTION_NAME)])

        self.assert_templates(
            [
                "utter_daily_ci__recommendations__more_information_vulnerable_population",
                "utter_daily_ci__recommendations__tomorrow_ci",
                "utter_daily_ci__recommendations__recommendation_1",
                "utter_daily_ci__recommendations__recommendation_2",
            ]
        )

    def test_general_population__not_has_211(self):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: False,
                PRECONDITIONS_SLOT: False,
                PROVINCE_SLOT: "xyz",
            },
        )

        self.run_action(tracker)

        self.assert_events([FollowupAction(GOODBYE_ACTION_NAME)])

        self.assert_templates(
            [
                "utter_daily_ci__recommendations__more_information_general",
                "utter_daily_ci__recommendations__tomorrow_ci",
                "utter_daily_ci__recommendations__recommendation_1",
                "utter_daily_ci__recommendations__recommendation_2",
            ]
        )

    def test_age_over_65__no_preconditions__has_211_other_province(self):
        self._test_vulnerable_population__has_211_other_province(
            age_over_65=True, preconditions=False
        )

    def test_age_over_65__preconditions__has_211_other_province(self):
        self._test_vulnerable_population__has_211_other_province(
            age_over_65=True, preconditions=True
        )

    def test_not_age_over_65__preconditions__has_211_other_province(self):
        self._test_vulnerable_population__has_211_other_province(
            age_over_65=False, preconditions=True
        )

    def _test_vulnerable_population__has_211_other_province(
        self, age_over_65: bool, preconditions: bool
    ):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: age_over_65,
                PRECONDITIONS_SLOT: preconditions,
                PROVINCE_SLOT: "bc",
            },
        )

        self.run_action(tracker)

        self.assert_events([FollowupAction(GOODBYE_ACTION_NAME)])

        self.assert_templates(
            [
                "utter_daily_ci__recommendations__more_information_vulnerable_population",
                "utter_daily_ci__recommendations__211_other_provinces",
                "utter_daily_ci__recommendations__tomorrow_ci",
                "utter_daily_ci__recommendations__recommendation_1",
                "utter_daily_ci__recommendations__recommendation_2",
            ]
        )

    def test_general__has_211_other_province(self):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: False,
                PRECONDITIONS_SLOT: False,
                PROVINCE_SLOT: "bc",
            },
        )

        self.run_action(tracker)

        self.assert_events([FollowupAction(GOODBYE_ACTION_NAME)])

        self.assert_templates(
            [
                "utter_daily_ci__recommendations__more_information_general",
                "utter_daily_ci__recommendations__211_other_provinces",
                "utter_daily_ci__recommendations__tomorrow_ci",
                "utter_daily_ci__recommendations__recommendation_1",
                "utter_daily_ci__recommendations__recommendation_2",
            ]
        )

    def test_age_over_65__no_preconditions__has_211_qc(self):
        self._test_vulnerable_population__has_211_qc(
            age_over_65=True, preconditions=False
        )

    def test_age_over_65__preconditions__has_211_qc(self):
        self._test_vulnerable_population__has_211_qc(
            age_over_65=True, preconditions=True
        )

    def test_not_age_over_65__preconditions__has_211_qc(self):
        self._test_vulnerable_population__has_211_qc(
            age_over_65=False, preconditions=True
        )

    def _test_vulnerable_population__has_211_qc(
        self, age_over_65: bool, preconditions: bool
    ):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: age_over_65,
                PRECONDITIONS_SLOT: preconditions,
                PROVINCE_SLOT: "qc",
            },
        )

        self.run_action(tracker)

        self.assert_events([FollowupAction(GOODBYE_ACTION_NAME)])

        self.assert_templates(
            [
                "utter_daily_ci__recommendations__more_information_vulnerable_population",
                "utter_daily_ci__recommendations__211_qc",
                "utter_daily_ci__recommendations__tomorrow_ci",
                "utter_daily_ci__recommendations__recommendation_1",
                "utter_daily_ci__recommendations__recommendation_2",
            ]
        )

    def test_general__has_211_qc(self):
        tracker = self.create_tracker(
            slots={
                AGE_OVER_65_SLOT: False,
                PRECONDITIONS_SLOT: False,
                PROVINCE_SLOT: "qc",
            },
        )

        self.run_action(tracker)

        self.assert_events([FollowupAction(GOODBYE_ACTION_NAME)])

        self.assert_templates(
            [
                "utter_daily_ci__recommendations__more_information_general",
                "utter_daily_ci__recommendations__211_qc",
                "utter_daily_ci__recommendations__tomorrow_ci",
                "utter_daily_ci__recommendations__recommendation_1",
                "utter_daily_ci__recommendations__recommendation_2",
            ]
        )
