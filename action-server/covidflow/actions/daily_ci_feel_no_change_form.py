from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.constants import (
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .lib.log_util import bind_logger

FORM_NAME = "daily_ci_feel_no_change_form"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"

ASK_HAS_COUGH_ACTION_NAME = f"action_ask_{FORM_NAME}_{HAS_COUGH_SLOT}"
ASK_HAS_FEVER_ACTION_NAME = f"action_ask_{FORM_NAME}_{HAS_FEVER_SLOT}"


class ActionAskDailyCiFeelNoChangeFormHasFever(Action):
    def name(self) -> Text:

        return ASK_HAS_FEVER_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        template_name = f"utter_ask_{FORM_NAME}_{HAS_FEVER_SLOT}"

        if tracker.get_slot(LAST_HAS_FEVER_SLOT) is True:
            dispatcher.utter_message(template=f"{template_name}___still")
        else:
            dispatcher.utter_message(template=template_name)

        return []


class ActionAskDailyCiFeelNoChangeFormHasCough(Action):
    def name(self) -> Text:

        return ASK_HAS_COUGH_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        template_name = f"utter_ask_{FORM_NAME}_{HAS_COUGH_SLOT}"

        if tracker.get_slot(LAST_HAS_COUGH_SLOT) is True:
            dispatcher.utter_message(template=f"{template_name}___still")
        else:
            dispatcher.utter_message(template=template_name)

        return []


class ValidateDailyCiFeelNoChangeForm(Action):
    def name(self) -> Text:

        return VALIDATE_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        extracted_slots: Dict[Text, Any] = tracker.form_slots_to_validate()

        validation_events: List[EventType] = []
        for slot_name, slot_value in extracted_slots.items():
            slot_events = [SlotSet(slot_name, slot_value)]

            if slot_name == HAS_FEVER_SLOT:
                slot_events += _validate_has_fever(slot_value, dispatcher)
            elif slot_name == HAS_COUGH_SLOT:
                slot_events += _validate_has_cough(slot_value, dispatcher)
                if (
                    tracker.get_slot(LAST_SYMPTOMS_SLOT) == Symptoms.MILD
                ):  # Stop there if symptoms were mild
                    slot_events.extend(
                        [
                            SlotSet(REQUESTED_SLOT, None),
                            SlotSet(HAS_DIFF_BREATHING_SLOT, SKIP_SLOT_PLACEHOLDER),
                        ]
                    )
                    dispatcher.utter_message(
                        template="utter_daily_ci_feel_no_change_form_mild_last_symptoms_recommendation"
                    )
            elif slot_name == HAS_DIFF_BREATHING_SLOT:
                slot_events += _validate_has_diff_breathing(
                    slot_value, dispatcher, tracker
                )

            validation_events.extend(slot_events)

        return validation_events


def _validate_has_fever(
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value is True:
        dispatcher.utter_message(template="utter_daily_ci__acknowledge_fever")
        dispatcher.utter_message(template="utter_daily_ci__take_acetaminophen")
        dispatcher.utter_message(template="utter_daily_ci__avoid_ibuprofen")
    else:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_no_change_form_acknowledge_no_fever"
        )

    return []


def _validate_has_cough(
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value is True:
        dispatcher.utter_message(template="utter_daily_ci__cough_syrup_may_help")
        dispatcher.utter_message(template="utter_daily_ci__cough_syrup_pharmacist")
    else:
        dispatcher.utter_message(template="utter_daily_ci__acknowledge_no_cough")

    return []


def _validate_has_diff_breathing(
    value: bool, dispatcher: CollectingDispatcher, tracker: Tracker
) -> List[EventType]:
    slots = []

    if value is True:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_no_change_form_acknowledge_diff_breathing"
        )
        dispatcher.utter_message(
            template="utter_daily_ci_feel_no_change_form_diff_breathing_recommendation"
        )
    else:
        if (
            tracker.get_slot(HAS_FEVER_SLOT) is False
            and tracker.get_slot(HAS_COUGH_SLOT) is False
        ):
            slots.append(SlotSet(SYMPTOMS_SLOT, Symptoms.MILD))

        dispatcher.utter_message(
            template="utter_daily_ci_feel_no_change_form_acknowledge_no_diff_breathing"
        )
        dispatcher.utter_message(
            template="utter_daily_ci_feel_no_change_form_no_diff_breathing_recommendation"
        )

    return slots
