from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.assessment_common import AssessmentCommon, AssessmentSlots

CONTACT_RISK_SLOT = "has_contact_risk"


class AssessmentForm(FormAction):
    def name(self) -> Text:

        return "assessment_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        base_assessment_slots = AssessmentCommon.base_required_slots(tracker)

        # When we don't display self-isolation messages
        if (
            tracker.get_slot(AssessmentSlots.SEVERE_SYMPTOMS) is True
            or tracker.get_slot(AssessmentSlots.TRAVEL) is False
        ):
            return base_assessment_slots

        # conditional mild symptoms-contact-travel logic
        if tracker.get_slot(AssessmentSlots.HAS_COUGH) is False:
            base_assessment_slots.append(AssessmentSlots.CONTACT)
        if tracker.get_slot(AssessmentSlots.CONTACT) is False:
            base_assessment_slots.append(AssessmentSlots.TRAVEL)

        base_assessment_slots.append(AssessmentSlots.LIVES_ALONE)
        return base_assessment_slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return AssessmentCommon.slot_mappings(self)

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
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_symptoms_self_isolate")

        return {AssessmentSlots.MODERATE_SYMPTOMS: value}

    def validate_has_cough(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_symptoms_self_isolate")

        return {AssessmentSlots.HAS_COUGH: value}

    def validate_contact(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_contact_risk_self_isolate")

        return {AssessmentSlots.CONTACT: value}

    def validate_travel(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_contact_risk_self_isolate")

        return {AssessmentSlots.TRAVEL: value}

    def validate_lives_alone(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return AssessmentCommon.validate_lives_alone(value, dispatcher)

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if (
            tracker.get_slot(AssessmentSlots.CONTACT) is True
            or tracker.get_slot(AssessmentSlots.TRAVEL) is True
        ):
            return [SlotSet(CONTACT_RISK_SLOT, True,)] + AssessmentCommon.submit(
                self, dispatcher, tracker, domain
            )

        return AssessmentCommon.submit(self, dispatcher, tracker, domain)
