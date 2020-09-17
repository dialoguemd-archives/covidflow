from typing import Any, Dict, List, Optional, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionReverted, EventType, FollowupAction
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import ACTION_LISTEN_NAME

from .action_default_fallback import ACTION_NAME as FALLBACK_ACTION_NAME
from .lib.action_utils import get_intent
from .lib.log_util import bind_logger

logger = structlog.get_logger()

MAIN_INTENTS = [
    "get_assessment",
    "ask_question",
    "navigate_test_locations",
    "nlu_fallback",
]

SUPPORTED_INTENTS_BY_ACTION = {
    "action_greeting_messages": MAIN_INTENTS,
    "utter_ask_test_navigation__continue": [
        "get_assessment",
        "ask_question",
        "nlu_fallback",
    ],
    "action_test_navigation__anything_else": [
        "get_assessment",
        "ask_question",
        "nlu_fallback",
    ],
    "utter_ask_another_question": MAIN_INTENTS,
    "utter_ask_different_question": MAIN_INTENTS,
    "utter_ask_assess_to_answer": ["get_assessment", "ask_question", "nlu_fallback"],
    "utter_ask_assess_after_error": [
        "get_assessment",
        "navigate_test_locations",
        "nlu_fallback",
    ],
    "utter_ask_daily_checkin__invalid_id__want_assessment": MAIN_INTENTS,
    "utter_ask_daily_checkin__invalid_id__anything_else": MAIN_INTENTS,
    "utter_ask_anything_else_with_test_navigation": MAIN_INTENTS,
    "utter_ask_anything_else_without_test_navigation": MAIN_INTENTS,
}

ACTION_NAME = "action_check_task_allowed"


class ActionCheckTaskAllowed(Action):
    def name(self) -> Text:
        return ACTION_NAME  # We could call it otherwise when https://github.com/RasaHQ/rasa/issues/6516 will be solved

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        bind_logger(tracker)

        last_action = _get_last_action_name(tracker)
        logger.warn(last_action)
        intent = get_intent(tracker)
        if (
            last_action in SUPPORTED_INTENTS_BY_ACTION
            and intent in SUPPORTED_INTENTS_BY_ACTION[last_action]
        ):
            return []

        logger.debug(
            f'"{intent}" is not supported after action {last_action}. Triggering fallback'
        )
        return [ActionReverted(), FollowupAction(FALLBACK_ACTION_NAME)]


def _get_last_action_name(tracker: Tracker) -> Optional[str]:
    last_action = tracker.get_last_event_for(
        "action", exclude=[ACTION_LISTEN_NAME, FALLBACK_ACTION_NAME]
    )
    return last_action["name"] if last_action is not None else None
