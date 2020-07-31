import copy
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, UserUtteranceReverted, UserUttered
from rasa_sdk.executor import CollectingDispatcher

from .lib.log_util import bind_logger

ACTION_NAME = "action_unsupported_intent"


class ActionUnsupportedIntent(Action):
    def name(self) -> Text:
        return ACTION_NAME

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)

        last_user_event = tracker.get_last_event_for("user")
        last_user_event = copy.deepcopy(last_user_event)
        text = last_user_event["text"]

        fallback_user_event = UserUttered(
            text,
            parse_data={
                "text": text,
                "intent": {"name": "nlu_fallback", "confidence": 1.0},
                "intent_ranking": [{"name": "nlu_fallback", "confidence": 1.0}],
                "entities": [],
            },
        )

        return [
            UserUtteranceReverted(),
            ActionExecuted("action_listen"),
            fallback_user_event,
        ]
