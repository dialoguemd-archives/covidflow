from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from covidflow.actions.lib.log_util import bind_logger

ACTION_NAME = "action_ask_province_code"


class ActionAskProvinceCode(Action):
    def name(self) -> Text:
        return "action_ask_province_code"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        dispatcher.utter_message(template="utter_pre_ask_province_code")
        dispatcher.utter_message(template="utter_ask_province_code")

        return []
