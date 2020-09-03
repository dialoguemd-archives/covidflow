from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher

from covidflow.actions.lib.log_util import bind_logger
from covidflow.constants import PROVINCE_SLOT, PROVINCES

FORM_NAME = "province_age_form"
ACTION_NAME = f"validate_{FORM_NAME}"


class ValidateProvinceAgeForm(Action):
    def name(self) -> Text:
        return ACTION_NAME

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)
        extracted_slots: Dict[Text, Any] = tracker.form_slots_to_validate()

        validation_events = []

        for slot_name, slot_value in extracted_slots.items():
            if slot_name == PROVINCE_SLOT and slot_value not in PROVINCES:
                validation_events.append(SlotSet(PROVINCE_SLOT, None))
            else:
                validation_events.append(SlotSet(slot_name, slot_value))

        return validation_events
