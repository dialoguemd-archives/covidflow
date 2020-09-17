from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from .lib.log_util import bind_logger


class ActionGreetingMessages(Action):
    def name(self) -> Text:
        return "action_greeting_messages"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        dispatcher.utter_message(template="utter_greet")
        dispatcher.utter_message(template="utter_greet_warning")
        dispatcher.utter_message(template="utter_greet_options")
        dispatcher.utter_message(template="utter_ask_how_may_i_help")

        return []
