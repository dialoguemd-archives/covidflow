from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from covidflow.constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    LIVES_ALONE_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
)

from .assessment_common import AssessmentCommon
from .lib.form_helper import (
    request_next_slot,
    validate_boolean_slot,
    yes_no_nlu_mapping,
)
from .lib.log_util import bind_logger

FORM_NAME = "tested_positive_form"

MILD_SYMPTOMS_WORSENED_SLOT = "tested_positive__mild_symptoms_worsened"


class TestedPositiveForm(FormAction, AssessmentCommon):
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
        if tracker.active_form.get("name") != FORM_NAME:
            dispatcher.utter_message(template="utter_tested_positive_entry")
            dispatcher.utter_message(template="utter_tested_positive_self_isolate")
        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        slots: List[str] = [LIVES_ALONE_SLOT, SEVERE_SYMPTOMS_SLOT]

        if tracker.get_slot(SEVERE_SYMPTOMS_SLOT) is False:
            slots += [
                PROVINCE_SLOT,
                AGE_OVER_65_SLOT,
                HAS_FEVER_SLOT,
                MODERATE_SYMPTOMS_SLOT,
            ]

            if tracker.get_slot(MODERATE_SYMPTOMS_SLOT) is False:
                slots += [HAS_COUGH_SLOT]

                if (
                    tracker.get_slot(HAS_COUGH_SLOT) is True
                    or tracker.get_slot(HAS_FEVER_SLOT) is True
                ):
                    slots += [MILD_SYMPTOMS_WORSENED_SLOT]

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            **AssessmentCommon.base_slot_mappings(self),
            MILD_SYMPTOMS_WORSENED_SLOT: yes_no_nlu_mapping(self),
        }

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        return request_next_slot(self, dispatcher, tracker, domain, None)

    def validate_moderate_symptoms(
        self,
        value: Union[Text, bool],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        result = super().validate_moderate_symptoms(value, dispatcher, tracker, domain)

        if value is True:
            dispatcher.utter_message(
                template="utter_symptoms_worsen_emergency_assistance"
            )

        return result

    def validate_lives_alone(
        self,
        value: Union[bool, str],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        result = super().validate_lives_alone(value, dispatcher, tracker, domain)
        if isinstance(value, bool):
            dispatcher.utter_message(template="utter_assess_symptoms")
        return result

    @validate_boolean_slot
    def validate_tested_positive__mild_symptoms_worsened(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(
                template="utter_symptoms_worsen_emergency_assistance"
            )

        return {MILD_SYMPTOMS_WORSENED_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return AssessmentCommon.base_submit(self, dispatcher, tracker, domain)
