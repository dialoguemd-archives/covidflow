from typing import Any, Dict, List, Text, Union, cast

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    LIVES_ALONE_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SYMPTOMS_SLOT,
)
from .lib.provincial_811 import get_provincial_811


class AssessmentCommon:
    @staticmethod
    def base_required_slots(tracker: Tracker) -> List[Text]:
        slots: List[str] = [SEVERE_SYMPTOMS_SLOT]

        if tracker.get_slot(SEVERE_SYMPTOMS_SLOT) is False:
            slots += [
                PROVINCE_SLOT,
                AGE_OVER_65_SLOT,
                HAS_FEVER_SLOT,
                MODERATE_SYMPTOMS_SLOT,
            ]

            if tracker.get_slot(MODERATE_SYMPTOMS_SLOT) is False:
                slots += [HAS_COUGH_SLOT]

        return cast(List[str], slots)

    @staticmethod
    def slot_mappings(form: FormAction) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            AGE_OVER_65_SLOT: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            SEVERE_SYMPTOMS_SLOT: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            HAS_FEVER_SLOT: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            MODERATE_SYMPTOMS_SLOT: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            HAS_COUGH_SLOT: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            LIVES_ALONE_SLOT: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
        }

    @staticmethod
    def validate_province(value: Text, domain: Dict[Text, Any],) -> Dict[Text, Any]:
        provincial_811 = get_provincial_811(value, domain)

        return {
            PROVINCE_SLOT: value,
            PROVINCIAL_811_SLOT: provincial_811,
        }

    @staticmethod
    def validate_lives_alone(
        value: bool, dispatcher: CollectingDispatcher,
    ) -> Dict[Text, Any]:

        if value is True:
            dispatcher.utter_message(template="utter_dont_leave_home")
        else:
            dispatcher.utter_message(template="utter_stay_separate_room")
            dispatcher.utter_message(template="utter_distance_clean_surfaces")
            dispatcher.utter_message(template="utter_wear_mask_same_room")

        dispatcher.utter_message(template="utter_self_isolation_link")

        return {LIVES_ALONE_SLOT: value}

    @staticmethod
    def submit(
        form: FormAction,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        symptoms_value = _get_symptoms_value(tracker)

        return [
            SlotSet(SYMPTOMS_SLOT, symptoms_value),
            SlotSet(SELF_ASSESS_DONE_SLOT, True),
        ]


def _get_symptoms_value(tracker: Tracker) -> str:
    symptoms_value = "none"
    if tracker.get_slot(SEVERE_SYMPTOMS_SLOT):
        symptoms_value = "severe"
    elif tracker.get_slot(MODERATE_SYMPTOMS_SLOT):
        symptoms_value = "moderate"
    elif tracker.get_slot(HAS_COUGH_SLOT) or tracker.get_slot(HAS_FEVER_SLOT):
        symptoms_value = "mild"

    return symptoms_value
