from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .lib.log_util import bind_logger


class ActionTestedPositiveMaybeCuredFinalRecommendations(Action):
    def name(self) -> Text:
        return "action_tested_positive_maybe_cured_final_recommendations"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        dispatcher.utter_message(template="utter_maybe_recovered")
        dispatcher.utter_message(template="utter_more_information")

        return []
