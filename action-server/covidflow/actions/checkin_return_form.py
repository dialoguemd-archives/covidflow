from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .assessment_common import AssessmentCommon
from .constants import (
    AGE_OVER_65_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    MODERATE_SYMPTOMS_SLOT,
    PROVINCE_SLOT,
    SEVERE_SYMPTOMS_SLOT,
)
from .lib.log_util import bind_logger

FORM_NAME = "checkin_return_form"

MODERATE_SYMPTOMS_WORSENED_SLOT = "checkin_return__moderate_symptoms_worsened"


class CheckinReturnForm(FormAction):
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
            dispatcher.utter_message(template="utter_returning_for_checkin")

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        slots: List[str] = [SEVERE_SYMPTOMS_SLOT]

        if tracker.get_slot(SEVERE_SYMPTOMS_SLOT) is False:
            slots += [
                PROVINCE_SLOT,
                AGE_OVER_65_SLOT,
                HAS_FEVER_SLOT,
                MODERATE_SYMPTOMS_SLOT,
            ]

            if tracker.get_slot(MODERATE_SYMPTOMS_SLOT) is True:
                slots += [MODERATE_SYMPTOMS_WORSENED_SLOT]
            else:
                slots += [HAS_COUGH_SLOT]

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            **AssessmentCommon.slot_mappings(self),
            MODERATE_SYMPTOMS_WORSENED_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
        }

    def validate_severe_symptoms(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return AssessmentCommon.validate_severe_symptoms(value, dispatcher)

    def validate_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return AssessmentCommon.validate_province(value, domain)

    def validate_moderate_symptoms(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return AssessmentCommon.validate_moderate_symptoms(value, dispatcher)

    def validate_checkin_return__moderate_symptoms_worsened(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_contact_healthcare_professional")
            dispatcher.utter_message(
                template="utter_contact_healthcare_professional_options"
            )

        dispatcher.utter_message(template="utter_symptoms_worsen_emergency")

        return {MODERATE_SYMPTOMS_WORSENED_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if (
            tracker.get_slot(MODERATE_SYMPTOMS_SLOT) is True
            or tracker.get_slot(HAS_COUGH_SLOT) is True
            or tracker.get_slot(HAS_FEVER_SLOT) is True
        ):
            dispatcher.utter_message(template="utter_returning_self_isolate")
            dispatcher.utter_message(template="utter_self_isolation_link")

        return AssessmentCommon.submit(self, dispatcher, tracker, domain)
