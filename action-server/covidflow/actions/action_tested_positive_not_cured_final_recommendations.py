from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .lib.log_util import bind_logger


class ActionTestedPositiveNotCuredFinalRecommendations(Action):
    def name(self) -> Text:
        return "action_tested_positive_not_cured_final_recommendations"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        dispatcher.utter_message(template="utter_remind_monitor_symptoms_temperature")
        dispatcher.utter_message(template="utter_remind_possible_checkin")

        return []
