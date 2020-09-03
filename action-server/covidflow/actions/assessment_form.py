from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from covidflow.constants import (
    CONTACT_SLOT,
    HAS_CONTACT_RISK_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    LIVES_ALONE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    TRAVEL_SLOT,
)

from .assessment_common import AssessmentCommon
from .lib.form_helper import (
    request_next_slot,
    validate_boolean_slot,
    yes_no_nlu_mapping,
)
from .lib.log_util import bind_logger

FORM_NAME = "assessment_form"


class AssessmentForm(FormAction, AssessmentCommon):
    def name(self) -> Text:

        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

    ## override to play initial message
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_loop.get("name") != FORM_NAME:
            dispatcher.utter_message(template="utter_assessment_entry")

        return await super()._activate_if_required(dispatcher, tracker, domain)

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        return request_next_slot(self, dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        base_assessment_slots = AssessmentCommon.base_required_slots(tracker)

        # When we don't display self-isolation messages
        if (
            tracker.get_slot(SEVERE_SYMPTOMS_SLOT) is True
            or tracker.get_slot(TRAVEL_SLOT) is False
        ):
            return base_assessment_slots

        # conditional mild symptoms-contact-travel logic
        if (
            tracker.get_slot(HAS_COUGH_SLOT) is False
            and tracker.get_slot(HAS_FEVER_SLOT) is False
        ):
            base_assessment_slots.append(CONTACT_SLOT)
        if tracker.get_slot(CONTACT_SLOT) is False:
            base_assessment_slots.append(TRAVEL_SLOT)

        base_assessment_slots.append(LIVES_ALONE_SLOT)
        return base_assessment_slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            **AssessmentCommon.base_slot_mappings(self),
            CONTACT_SLOT: yes_no_nlu_mapping(self),
            TRAVEL_SLOT: yes_no_nlu_mapping(self),
        }

    def validate_moderate_symptoms(
        self,
        value: Union[Text, bool],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        result = super().validate_moderate_symptoms(value, dispatcher, tracker, domain)

        if value is True:
            dispatcher.utter_message(template="utter_moderate_symptoms_self_isolate")

        return result

    def validate_has_cough(
        self,
        value: Union[Text, bool],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True or (
            value is False and tracker.get_slot(HAS_FEVER_SLOT) is True
        ):
            dispatcher.utter_message(template="utter_mild_symptoms_self_isolate")

        return super().validate_has_cough(value, dispatcher, tracker, domain)

    @validate_boolean_slot
    def validate_contact(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_contact_risk_self_isolate")

        return {CONTACT_SLOT: value}

    @validate_boolean_slot
    def validate_travel(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_contact_risk_self_isolate")

        return {TRAVEL_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if (
            tracker.get_slot(CONTACT_SLOT) is True
            or tracker.get_slot(TRAVEL_SLOT) is True
        ):
            return [
                SlotSet(HAS_CONTACT_RISK_SLOT, True)
            ] + AssessmentCommon.base_submit(self, dispatcher, tracker, domain)

        return AssessmentCommon.base_submit(self, dispatcher, tracker, domain)
