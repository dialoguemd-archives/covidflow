from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionSuspectModerateSymptomsRecommendations(Action):
    def name(self) -> Text:
        return "action_suspect_moderate_symptoms_recommendations"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_symptoms_worsen_emergency")
        dispatcher.utter_message(template="utter_monitor_symptoms_assistance")

        return []
