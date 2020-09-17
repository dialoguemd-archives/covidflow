import copy
from typing import Any, Dict, List, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import (
    ActionExecuted,
    EventType,
    FollowupAction,
    UserUtteranceReverted,
    UserUttered,
)
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import ACTION_LISTEN_NAME, FALLBACK_INTENT

from .lib.action_utils import get_intent
from .lib.log_util import bind_logger

logger = structlog.get_logger()

ERROR_SUFFIX = "_error"

ACTION_NAME = "action_default_fallback"  # We could call it otherwise when https://github.com/RasaHQ/rasa/issues/6516 will be solved


class ActionDefaultFallback(Action):
    """Core falblack action - triggered when no rule matched

    Replaces input by fallback intent (nlu_fallback)
    except if in a form or if input was already replaced (no error rule applied).
    In these cases the default behaviour is applied -
    playing the last message's error version ("{template_name}_error")
    """

    def name(self) -> Text:
        return ACTION_NAME

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        bind_logger(tracker)

        if get_intent(tracker) == FALLBACK_INTENT or tracker.active_loop != {}:
            logger.warn(get_intent(tracker))
            logger.warn(tracker.active_loop)
            return _replay_message_with_suffix(dispatcher, tracker)

        return _replace_user_input(tracker)


def _with_error_suffix(template_name: str) -> str:
    if template_name.endswith(ERROR_SUFFIX):
        return template_name
    else:
        return f"{template_name}{ERROR_SUFFIX}"


def _replay_message_with_suffix(
    dispatcher: CollectingDispatcher, tracker: Tracker
) -> List[EventType]:
    logger.debug(
        "No rule matched for intent, playing error version of last bot message"
    )
    latest_bot_message = tracker.get_last_event_for("bot")
    logger.warn(latest_bot_message)
    template = latest_bot_message["metadata"]["template_name"]
    dispatcher.utter_message(template=_with_error_suffix(template))

    return [UserUtteranceReverted(), FollowupAction(ACTION_LISTEN_NAME)]


def _replace_user_input(tracker: Tracker) -> List[EventType]:
    logger.debug(
        "No rule matched for intent, replacing user input with fallback intent"
    )
    last_user_event = tracker.get_last_event_for("user")
    last_user_event = copy.deepcopy(last_user_event)
    text = last_user_event["text"]

    fallback_user_event = UserUttered(
        text,
        parse_data={
            "text": text,
            "intent": {"name": FALLBACK_INTENT, "confidence": 1.0},
            "intent_ranking": [{"name": FALLBACK_INTENT, "confidence": 1.0}],
            "entities": [],
        },
    )

    return [
        UserUtteranceReverted(),
        ActionExecuted(ACTION_LISTEN_NAME),
        fallback_user_event,
    ]
