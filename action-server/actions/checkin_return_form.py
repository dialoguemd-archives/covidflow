from typing import Any, Dict, List, Text, Union, cast

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.assessment_common import AssessmentCommon, AssessmentSlots


class CheckinReturnForm(FormAction):
    def name(self) -> Text:

        return "checkin_return_form"

    ## override to play initial message
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_form.get("name") != "checkin_return_form":
            dispatcher.utter_message(template="utter_returning_for_checkin")

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        slots = [AssessmentSlots.SEVERE_SYMPTOMS]

        if tracker.get_slot(AssessmentSlots.SEVERE_SYMPTOMS) is False:
            slots += [
                AssessmentSlots.PROVINCE,
                AssessmentSlots.AGE_OVER_65,
                AssessmentSlots.HAS_FEVER,
                AssessmentSlots.LIVES_ALONE,
                AssessmentSlots.MODERATE_SYMPTOMS,
            ]

            if tracker.get_slot(AssessmentSlots.MODERATE_SYMPTOMS) is False:
                slots += [AssessmentSlots.HAS_COUGH]

        return cast(List[str], slots)

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return AssessmentCommon.slot_mappings(self)

    def validate_has_fever(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        dispatcher.utter_message(template="utter_symptoms_self_isolate")

        return {AssessmentSlots.HAS_FEVER: value}

    def validate_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return AssessmentCommon.validate_province(value, domain)

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return AssessmentCommon.submit(self, dispatcher, tracker, domain)
