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
    LAST_SYMPTOMS_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .lib.log_util import bind_logger

FORM_NAME = "daily_ci_feel_better_form"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"

HAS_OTHER_MILD_SYMPTOMS_SLOT = "daily_ci_feel_better_form_has_other_mild_symptoms"
IS_SYMPTOM_FREE_SLOT = "daily_ci_feel_better_form_is_symptom_free"

ASK_HAS_OTHER_MILD_SYMPTOMS_ACTION_NAME = f"action_ask_{HAS_OTHER_MILD_SYMPTOMS_SLOT}"
ASK_HAS_COUGH_ACTION_NAME = f"action_ask_{FORM_NAME}_{HAS_COUGH_SLOT}"


class ActionAskDailyCiFeelBetterFormHasCough(Action):
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


class ActionAskDailyCiFeelBetterFormHasOtherMildSymptoms(Action):
    def name(self) -> Text:

        return ASK_HAS_OTHER_MILD_SYMPTOMS_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        template_name = f"utter_ask_{HAS_OTHER_MILD_SYMPTOMS_SLOT}"

        if tracker.get_slot(LAST_SYMPTOMS_SLOT) == Symptoms.MODERATE:
            dispatcher.utter_message(template=f"{template_name}___with_acknowledge")
        else:
            dispatcher.utter_message(template=template_name)

        return []


class ValidateDailyCiFeelBetterForm(Action):
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
                    tracker.get_slot(LAST_SYMPTOMS_SLOT) != Symptoms.MODERATE
                ):  # Next slot only happens when symptoms are moderate
                    slot_events.append(
                        SlotSet(HAS_DIFF_BREATHING_SLOT, SKIP_SLOT_PLACEHOLDER)
                    )
            elif slot_name == HAS_DIFF_BREATHING_SLOT:
                slot_events += _validate_has_diff_breathing(slot_value, dispatcher)
            elif slot_name == HAS_OTHER_MILD_SYMPTOMS_SLOT:
                slot_events += _validate_has_other_mild_symptoms(
                    slot_value, dispatcher, tracker
                )
            elif slot_name == IS_SYMPTOM_FREE_SLOT:
                slot_events += _validate_is_symptom_free(slot_value, dispatcher)

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
            template="utter_daily_ci_feel_better_acknowledge_no_fever"
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
    value: bool, dispatcher: CollectingDispatcher,
) -> List[EventType]:
    if value is True:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_better_breathing_difficulty_recommendation_1"
        )
        dispatcher.utter_message(
            template="utter_daily_ci_feel_better_breathing_difficulty_recommendation_2"
        )
        return [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_OTHER_MILD_SYMPTOMS_SLOT, SKIP_SLOT_PLACEHOLDER),
            SlotSet(IS_SYMPTOM_FREE_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]  # Récupérer le cossin de l'autre
    else:
        return [SlotSet(SYMPTOMS_SLOT, Symptoms.MILD)]


def _validate_has_other_mild_symptoms(
    value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
) -> List[EventType]:
    if (
        value is True
        or tracker.get_slot(HAS_FEVER_SLOT) is True
        or tracker.get_slot(HAS_COUGH_SLOT) is True
    ):
        dispatcher.utter_message(
            template="utter_daily_ci_feel_better_form_has_other_mild_symptoms_recommendation"
        )
        return [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(IS_SYMPTOM_FREE_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

    return []


def _validate_is_symptom_free(
    value: Text, dispatcher: CollectingDispatcher,
) -> List[EventType]:

    if value is True:
        return [SlotSet(SYMPTOMS_SLOT, Symptoms.NONE)]
    else:
        dispatcher.utter_message(
            template="utter_daily_ci_feel_better_form_has_other_mild_symptoms_still_sick_recommendation"
        )
        return []
