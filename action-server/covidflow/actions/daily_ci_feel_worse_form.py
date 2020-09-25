from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.constants import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .lib.form_helper import end_form_additional_events
from .lib.log_util import bind_logger

FORM_NAME = "daily_ci_feel_worse_form"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"

HAS_DIFF_BREATHING_WORSENED_SLOT = (
    "daily_ci_feel_worse_form_has_diff_breathing_worsened"
)

ASK_HAS_COUGH_ACTION_NAME = f"action_ask_{FORM_NAME}_{HAS_COUGH_SLOT}"
ASK_HAS_DIFF_BREATHING_ACTION_NAME = f"action_ask_{FORM_NAME}_{HAS_DIFF_BREATHING_SLOT}"

ORDERED_FORM_SLOTS = [
    SEVERE_SYMPTOMS_SLOT,
    HAS_FEVER_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_DIFF_BREATHING_WORSENED_SLOT,
    HAS_COUGH_SLOT,
]


class ActionAskDailyCiFeelWorseFormHasDiffBreathing(Action):
    def name(self) -> Text:

        return ASK_HAS_DIFF_BREATHING_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        template_name = f"utter_ask_{FORM_NAME}_{HAS_DIFF_BREATHING_SLOT}"

        if tracker.get_slot(LAST_HAS_DIFF_BREATHING_SLOT) is True:
            dispatcher.utter_message(template=f"{template_name}___still")
        else:
            dispatcher.utter_message(template=template_name)

        return []


class ActionAskDailyCiFeelWorseFormHasCough(Action):
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


class ActionSetFeelWorseTrue(Action):
    def name(self) -> Text:

        return "action_set_feel_worse_true"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        return [SlotSet(FEEL_WORSE_SLOT, True)]


class ValidateDailyCiFeelWorseForm(Action):
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

            if slot_name == SEVERE_SYMPTOMS_SLOT:
                slot_events += _validate_severe_symptoms(slot_value, dispatcher)
            elif slot_name == HAS_FEVER_SLOT:
                slot_events += _validate_has_fever(slot_value, dispatcher)
            elif slot_name == HAS_DIFF_BREATHING_SLOT:
                slot_events += _validate_has_diff_breathing(slot_value, dispatcher)
            elif slot_name == HAS_DIFF_BREATHING_WORSENED_SLOT:
                slot_events += _validate_has_diff_breathing_worsened(
                    slot_value, dispatcher
                )
            elif slot_name == HAS_COUGH_SLOT:
                slot_events += _validate_has_cough(slot_value, dispatcher)

            validation_events.extend(slot_events)

        return validation_events


def _validate_severe_symptoms(
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value is True:
        return [
            SlotSet(SYMPTOMS_SLOT, Symptoms.SEVERE),
            SlotSet(REQUESTED_SLOT, None),
        ] + end_form_additional_events(SEVERE_SYMPTOMS_SLOT, ORDERED_FORM_SLOTS)

    dispatcher.utter_message(
        template="utter_daily_ci_feel_worse_acknowledge_no_severe_symptoms"
    )
    return []


def _validate_has_fever(
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value is True:
        dispatcher.utter_message(template="utter_daily_ci__acknowledge_fever")
        dispatcher.utter_message(template="utter_daily_ci__take_acetaminophen")
        dispatcher.utter_message(template="utter_daily_ci__avoid_ibuprofen")
    else:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_acknowledge_no_fever"
        )

    return []


def _validate_has_diff_breathing(
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value == False:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_acknowledge_no_diff_breathing"
        )
        return [SlotSet(HAS_DIFF_BREATHING_WORSENED_SLOT, SKIP_SLOT_PLACEHOLDER)]

    return [SlotSet(HAS_COUGH_SLOT, SKIP_SLOT_PLACEHOLDER)]


def _validate_has_diff_breathing_worsened(
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value is True:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_diff_breathing_worsened_recommendation_1"
        )
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_diff_breathing_worsened_recommendation_2"
        )
    else:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_diff_breathing_not_worsened_recommendation_1"
        )
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_diff_breathing_not_worsened_recommendation_2"
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
        dispatcher.utter_message(
            template="utter_daily_ci_feel_worse_no_cough_recommendation"
        )

    return []
