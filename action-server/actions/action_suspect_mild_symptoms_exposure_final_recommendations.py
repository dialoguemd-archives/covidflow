from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionSuspectMildSymptomsExposureFinalRecommendations(Action):
    def name(self) -> Text:
        return "action_suspect_mild_symptoms_exposure_final_recommendations"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_remind_stay_home_self_isolate")
        dispatcher.utter_message(template="utter_remind_possible_checkin")

        return []
