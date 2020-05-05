from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import FollowupAction
from rasa_sdk.executor import CollectingDispatcher

from actions.action_goodbye import ACTION_NAME as GOODBYE_ACTION_NAME
from actions.constants import PROVINCES_WITH_211

ACTION_NAME = "action_daily_ci_recommendations"

AGE_OVER_65_SLOT = "age_over_65"
PRECONDITIONS_SLOT = "preconditions"
PROVINCE_SLOT = "province"


class ActionDailyCiRecommendations(Action):
    def name(self) -> Text:
        return ACTION_NAME

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if (
            tracker.get_slot(AGE_OVER_65_SLOT) is True
            or tracker.get_slot(PRECONDITIONS_SLOT) is True
        ):
            dispatcher.utter_message(
                template="utter_daily_ci__recommendations__more_information_vulnerable_population"
            )
        else:
            dispatcher.utter_message(
                template="utter_daily_ci__recommendations__more_information_general"
            )

        if tracker.get_slot(PROVINCE_SLOT) in PROVINCES_WITH_211:
            if tracker.get_slot(PROVINCE_SLOT) == "qc":
                dispatcher.utter_message(
                    template="utter_daily_ci__recommendations__211_qc"
                )
            else:
                dispatcher.utter_message(
                    template="utter_daily_ci__recommendations__211_other_provinces"
                )

        dispatcher.utter_message(
            template="utter_daily_ci__recommendations__tomorrow_ci"
        )

        dispatcher.utter_message(
            template="utter_daily_ci__recommendations__recommendation_1"
        )

        dispatcher.utter_message(
            template="utter_daily_ci__recommendations__recommendation_2"
        )

        return [FollowupAction(GOODBYE_ACTION_NAME)]
