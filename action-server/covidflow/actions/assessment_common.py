from typing import Any, Dict, List, Text, Union, cast

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from covidflow.constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    LIVES_ALONE_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    PROVINCES,
    PROVINCIAL_811_SLOT,
    SELF_ASSESS_DONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .lib.form_helper import validate_boolean_slot, yes_no_nlu_mapping
from .lib.provincial_811 import get_provincial_811


class AssessmentCommon:
    """
    Represents common elements in the 3 assessment forms:
    - tested_positive_form
    - checkin_return_form
    - assessment_form

    Methods are mostly static due to Rasa's constraints with forms and inheritance,
    except for validators, that can be overwritten
    """

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
    def base_slot_mappings(form: FormAction) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            PROVINCE_SLOT: [form.from_entity(entity="province"), form.from_text()],
            AGE_OVER_65_SLOT: yes_no_nlu_mapping(form),
            SEVERE_SYMPTOMS_SLOT: yes_no_nlu_mapping(form),
            HAS_FEVER_SLOT: yes_no_nlu_mapping(form),
            MODERATE_SYMPTOMS_SLOT: yes_no_nlu_mapping(form),
            HAS_COUGH_SLOT: yes_no_nlu_mapping(form),
            LIVES_ALONE_SLOT: yes_no_nlu_mapping(form),
        }

    # province is asked after severe symptoms so the message can be added here
    @validate_boolean_slot
    def validate_severe_symptoms(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is False:
            dispatcher.utter_message(template="utter_pre_ask_province_code")

        return {SEVERE_SYMPTOMS_SLOT: value}

    def validate_province_code(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value not in PROVINCES:
            return {PROVINCE_SLOT: None}

        provincial_811 = get_provincial_811(value, domain)

        return {
            PROVINCE_SLOT: value,
            PROVINCIAL_811_SLOT: provincial_811,
        }

    @validate_boolean_slot
    def validate_age_over_65(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return {}

    @validate_boolean_slot
    def validate_has_fever(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return {}

    @validate_boolean_slot
    def validate_moderate_symptoms(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is False:
            dispatcher.utter_message(template="utter_moderate_symptoms_false")

        return {MODERATE_SYMPTOMS_SLOT: value}

    @validate_boolean_slot
    def validate_has_cough(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return {}

    @validate_boolean_slot
    def validate_lives_alone(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_lives_alone_true")
        else:
            dispatcher.utter_message(template="utter_lives_alone_false_1")
            dispatcher.utter_message(template="utter_lives_alone_false_2")
            dispatcher.utter_message(template="utter_lives_alone_false_3")

        dispatcher.utter_message(template="utter_self_isolation_final")

        return {LIVES_ALONE_SLOT: value}

    @staticmethod
    def base_submit(
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
    symptoms_value = Symptoms.NONE
    if tracker.get_slot(SEVERE_SYMPTOMS_SLOT):
        symptoms_value = Symptoms.SEVERE
    elif tracker.get_slot(MODERATE_SYMPTOMS_SLOT):
        symptoms_value = Symptoms.MODERATE
    elif tracker.get_slot(HAS_COUGH_SLOT) or tracker.get_slot(HAS_FEVER_SLOT):
        symptoms_value = Symptoms.MILD

    return symptoms_value
