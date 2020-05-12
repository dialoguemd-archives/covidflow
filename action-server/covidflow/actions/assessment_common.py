from enum import Enum
from typing import Any, Dict, List, Text, Union, cast

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .lib.provincial_811 import get_provincial_811

# isn't really an assessment slot, used for interpolation
PROVINCIAL_811_SLOT = "provincial_811"


class AssessmentSlots(str, Enum):
    SEVERE_SYMPTOMS = "severe_symptoms"
    MODERATE_SYMPTOMS = "moderate_symptoms"
    HAS_FEVER = "has_fever"
    PROVINCE = "province"
    AGE_OVER_65 = "age_over_65"
    HAS_COUGH = "has_cough"

    # From the self-isolation flow
    LIVES_ALONE = "lives_alone"

    # Optional, added by the calling form
    CONTACT = "contact"
    TRAVEL = "travel"

    RISK_LEVEL = "risk_level"
    SYMPTOMS = "symptoms"
    SELF_ASSESS_DONE = "self_assess_done"


class SelfIsolationPosition:
    START = "start"
    AFTER_FEVER = "after_fever"
    END = "end"


class AssessmentCommon:
    @staticmethod
    def base_required_slots(tracker: Tracker) -> List[Text]:
        slots = [AssessmentSlots.SEVERE_SYMPTOMS]

        if tracker.get_slot(AssessmentSlots.SEVERE_SYMPTOMS) is False:
            slots += [
                AssessmentSlots.PROVINCE,
                AssessmentSlots.AGE_OVER_65,
                AssessmentSlots.HAS_FEVER,
                AssessmentSlots.MODERATE_SYMPTOMS,
            ]

            if tracker.get_slot(AssessmentSlots.MODERATE_SYMPTOMS) is False:
                slots += [AssessmentSlots.HAS_COUGH]

        return cast(List[str], slots)

    @staticmethod
    def slot_mappings(form: FormAction) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            AssessmentSlots.AGE_OVER_65: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            AssessmentSlots.SEVERE_SYMPTOMS: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            AssessmentSlots.HAS_FEVER: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            AssessmentSlots.MODERATE_SYMPTOMS: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            AssessmentSlots.HAS_COUGH: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
            AssessmentSlots.LIVES_ALONE: [
                form.from_intent(intent="affirm", value=True),
                form.from_intent(intent="deny", value=False),
            ],
        }

    @staticmethod
    def validate_province(value: Text, domain: Dict[Text, Any],) -> Dict[Text, Any]:
        provincial_811 = get_provincial_811(value, domain)

        return {
            AssessmentSlots.PROVINCE: value,
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

        return {AssessmentSlots.LIVES_ALONE: value}

    @staticmethod
    def submit(
        form: FormAction,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        symptoms_value = _get_symptoms_value(tracker)

        return [
            SlotSet(AssessmentSlots.SYMPTOMS, symptoms_value),
            SlotSet(AssessmentSlots.SELF_ASSESS_DONE, True),
        ]


def _get_symptoms_value(tracker: Tracker) -> str:
    symptoms_value = "none"
    if tracker.get_slot(AssessmentSlots.SEVERE_SYMPTOMS):
        symptoms_value = "severe"
    elif tracker.get_slot(AssessmentSlots.MODERATE_SYMPTOMS):
        symptoms_value = "moderate"
    elif tracker.get_slot(AssessmentSlots.HAS_COUGH) or tracker.get_slot(
        AssessmentSlots.HAS_FEVER
    ):
        symptoms_value = "mild"

    return symptoms_value
