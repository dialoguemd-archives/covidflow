from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionReturningSymptomsNotWorsenedRecommendations(Action):
    def name(self) -> Text:
        return "action_returning_symptoms_not_worsened_recommendations"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_symptoms_worsen_emergency")
        dispatcher.utter_message(template="utter_returning_self_isolate")
        dispatcher.utter_message(template="utter_self_isolation_link")

        return []
