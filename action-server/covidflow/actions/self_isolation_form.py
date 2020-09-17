from typing import Any, Dict, List, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher

from covidflow.actions.lib.log_util import bind_logger
from covidflow.constants import LIVES_ALONE_SLOT

FORM_NAME = "self_isolation_form"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"

logger = structlog.get_logger()


class ValidateSelfIsolationForm(Action):
    def name(self) -> Text:
        return VALIDATE_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        extracted_slots: Dict[Text, Any] = tracker.form_slots_to_validate()

        if extracted_slots == {}:  # On activation
            return []

        if extracted_slots[LIVES_ALONE_SLOT] is True:
            dispatcher.utter_message(template="utter_lives_alone_true")
        else:
            dispatcher.utter_message(template="utter_lives_alone_false_1")
            dispatcher.utter_message(template="utter_lives_alone_false_2")
            dispatcher.utter_message(template="utter_lives_alone_false_3")

        dispatcher.utter_message(template="utter_self_isolation_final")

        return [SlotSet(LIVES_ALONE_SLOT, extracted_slots[LIVES_ALONE_SLOT])]
