from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionOfferDailyCheckin(Action):
    def name(self) -> Text:
        return "action_offer_daily_checkin"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_offer_checkin")
        dispatcher.utter_message(template="utter_explain_checkin_contact")
        dispatcher.utter_message(template="utter_explain_checkin_assessment")
        dispatcher.utter_message(template="utter_ask_want_checkin")

        return []
