from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionSetRiskLevel(Action):
    def name(self) -> Text:
        return "action_set_risk_level"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        risk_level = []
        if (
            tracker.get_slot("age_over_65") is True
            or tracker.get_slot("symptoms") == "moderate"
        ):
            risk_level.append("elevated-medical-risk")
        if tracker.get_slot("contact") is True or tracker.get_slot("travel") is True:
            risk_level.append("elevated-covid-risk")

        return [
            SlotSet(
                "risk_level", "common" if risk_level == [] else ",".join(risk_level)
            )
        ]
