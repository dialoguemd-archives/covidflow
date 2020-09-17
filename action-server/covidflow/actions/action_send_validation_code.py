from typing import Any, Dict, List, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher

from covidflow.utils.phone_number_validation import (
    FIRST_NAME_ENTITY,
    VALIDATION_CODE_ENTITY,
)

from .lib.log_util import bind_logger

logger = structlog.get_logger()


class ActionSendValidationCode(Action):
    def name(self) -> Text:
        return "action_send_validation_code"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        first_name = next(tracker.get_latest_entity_values(FIRST_NAME_ENTITY))
        validation_code = next(tracker.get_latest_entity_values(VALIDATION_CODE_ENTITY))

        logger.info(
            "Sending validation code: first_name=%s validation_code=%s",
            first_name,
            validation_code,
        )

        dispatcher.utter_message(
            template="utter_daily_checkin_validation_code",
            first_name=first_name,
            validation_code=validation_code,
        )

        return [Restarted()]
