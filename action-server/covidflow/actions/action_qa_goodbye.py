from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ConversationPaused
from rasa_sdk.executor import CollectingDispatcher

from .constants import CANCEL_CI_SLOT
from .lib.log_util import bind_logger


class ActionQaGoodbye(Action):
    def name(self) -> Text:
        return "action_qa_goodbye"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        if tracker.get_slot(CANCEL_CI_SLOT) is False:
            dispatcher.utter_message(
                template="utter_daily_ci__qa__will_contact_tomorrow"
            )

        dispatcher.utter_message(template="utter_goodbye")

        return [ConversationPaused()]
