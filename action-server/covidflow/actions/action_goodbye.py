from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ConversationPaused
from rasa_sdk.executor import CollectingDispatcher

from .constants import END_CONVERSATION_MESSAGE
from .lib.log_util import bind_logger

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
        bind_logger(tracker)
        dispatcher.utter_message(template="utter_goodbye")

        dispatcher.utter_message(json_message=END_CONVERSATION_MESSAGE)

        return [ConversationPaused()]
