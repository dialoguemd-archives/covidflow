from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ConversationPaused
from rasa_sdk.executor import CollectingDispatcher

ACTION_NAME = "action_goodbye"


class ActionGoodbye(Action):
    def name(self) -> Text:
        return ACTION_NAME

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(template="utter_goodbye")

        return [ConversationPaused()]
