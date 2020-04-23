from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionTestedPositiveNotCuredFinalRecommendations(Action):
    def name(self) -> Text:
        return "action_tested_positive_not_cured_final_recommendations"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            template="utter_acknowledge_remind_monitor_symptoms_temperature"
        )
        dispatcher.utter_message(template="utter_remind_possible_checkin")

        return []
