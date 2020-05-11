from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.assessment_common import AssessmentCommon, AssessmentSlots


class TestedPositiveForm(FormAction):
    def name(self) -> Text:

        return "tested_positive_form"

    ## override to play initial message
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_form.get("name") != "tested_positive_form":
            dispatcher.utter_message(template="utter_tested_positive_self_isolate")
        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return [
            AssessmentSlots.LIVES_ALONE.value
        ] + AssessmentCommon.base_required_slots(tracker)

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return AssessmentCommon.slot_mappings(self)

    def validate_lives_alone(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        result = AssessmentCommon.validate_lives_alone(value, dispatcher)
        dispatcher.utter_message(template="utter_assess_symptoms")
        return result

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
