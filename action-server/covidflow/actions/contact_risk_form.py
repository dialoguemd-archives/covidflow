from typing import Any, Dict, List, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.constants import (
    CONTACT_SLOT,
    HAS_CONTACT_RISK_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    TRAVEL_SLOT,
)

from .lib.log_util import bind_logger

FORM_NAME = "contact_risk_form"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"

logger = structlog.get_logger()


class ValidateContactRiskForm(Action):
    def name(self) -> Text:
        return VALIDATE_ACTION_NAME

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        extracted_slots: Dict[Text, Any] = tracker.form_slots_to_validate()

        validation_events: List[EventType] = []
        for slot_name, slot_value in extracted_slots.items():
            slot_events = [SlotSet(slot_name, slot_value)]

            if slot_name == CONTACT_SLOT and slot_value is True:
                slot_events += [
                    SlotSet(HAS_CONTACT_RISK_SLOT, True),
                    SlotSet(REQUESTED_SLOT, None),
                    SlotSet(TRAVEL_SLOT, SKIP_SLOT_PLACEHOLDER),
                ]
            if slot_name == TRAVEL_SLOT:
                slot_events += [SlotSet(HAS_CONTACT_RISK_SLOT, slot_value)]

            validation_events.extend(slot_events)

        return validation_events
