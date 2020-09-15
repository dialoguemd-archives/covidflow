from typing import Any, Dict, List, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.constants import (
    HAS_ASSISTANCE_SLOT,
    PROVINCE_SLOT,
    PROVINCES_WITH_211,
    SKIP_SLOT_PLACEHOLDER,
)

from .lib.log_util import bind_logger

FORM_NAME = "home_assistance_form"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"

logger = structlog.get_logger()


class ValidateHomeAssistanceForm(Action):
    def name(self) -> Text:
        return VALIDATE_ACTION_NAME

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        extracted_slots: Dict[Text, Any] = tracker.form_slots_to_validate()

        if extracted_slots == {}:  # On activation
            if not _has_211(tracker):
                _display_recommendations(False, dispatcher, tracker)

                return [
                    SlotSet(REQUESTED_SLOT, None),
                    SlotSet(HAS_ASSISTANCE_SLOT, SKIP_SLOT_PLACEHOLDER),
                ]
            return []

        if extracted_slots[HAS_ASSISTANCE_SLOT] is True:
            _display_recommendations(False, dispatcher, tracker)
        else:
            _display_recommendations(True, dispatcher, tracker)

        return [SlotSet(HAS_ASSISTANCE_SLOT, extracted_slots[HAS_ASSISTANCE_SLOT])]


def _has_211(tracker: Tracker) -> bool:
    province = tracker.get_slot(PROVINCE_SLOT)
    return province in PROVINCES_WITH_211


def _display_recommendations(
    propose_211: bool, dispatcher: CollectingDispatcher, tracker: Tracker
) -> None:
    if propose_211:
        dispatcher.utter_message(template="utter_home_assistance_offer_211_true_1")
        if tracker.get_slot(PROVINCE_SLOT) == "qc":
            dispatcher.utter_message(
                template="utter_home_assistance_offer_211_true_2_qc"
            )
        else:
            dispatcher.utter_message(
                template="utter_home_assistance_offer_211_true_2_other"
            )
        dispatcher.utter_message(template="utter_home_assistance_offer_211_true_3")
    else:
        dispatcher.utter_message(template="utter_home_assistance_offer_211_false")
    dispatcher.utter_message(template="utter_home_assistance_final")
