from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .constants import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    SYMPTOMS_SLOT,
)
from .daily_ci_assessment_common import submit_daily_ci_assessment
from .form_helper import request_next_slot

FORM_NAME = "daily_ci_feel_worse_form"

SEVERE_SYMPTOMS_SLOT = "severe_symptoms"
HAS_DIFF_BREATHING_WORSENED_SLOT = "daily_ci__feel_worse__has_diff_breathing_worsened"


class DailyCiFeelWorseForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    ## override to set feel_worse slot
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        events = []

        if tracker.active_form.get("name") != FORM_NAME:
            events.append(SlotSet(FEEL_WORSE_SLOT, True))

        return await super()._activate_if_required(dispatcher, tracker, domain) + events

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        slots = [SEVERE_SYMPTOMS_SLOT]

        if tracker.get_slot(SEVERE_SYMPTOMS_SLOT) is True:
            return slots

        slots += [HAS_FEVER_SLOT, HAS_DIFF_BREATHING_SLOT]

        if tracker.get_slot(HAS_DIFF_BREATHING_SLOT) is True:
            slots.append(HAS_DIFF_BREATHING_WORSENED_SLOT)
        else:
            slots.append(HAS_COUGH_SLOT)

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            SEVERE_SYMPTOMS_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            HAS_FEVER_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            HAS_DIFF_BREATHING_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            HAS_DIFF_BREATHING_WORSENED_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            HAS_COUGH_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
        }

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        return request_next_slot(
            self, dispatcher, tracker, domain, self._utter_ask_slot_template
        )

    def _utter_ask_slot_template(self, slot: str, tracker: Tracker) -> Optional[str]:
        if slot in [
            SEVERE_SYMPTOMS_SLOT,
            HAS_FEVER_SLOT,
            HAS_DIFF_BREATHING_SLOT,
            HAS_COUGH_SLOT,
        ]:
            return f"utter_ask_daily_ci__feel_worse__{slot}"

        return None

    def validate_severe_symptoms(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            return {SEVERE_SYMPTOMS_SLOT: value, SYMPTOMS_SLOT: "severe"}

        dispatcher.utter_message(
            template="utter_daily_ci__feel_worse__acknowledge_no_severe_symptoms"
        )
        return {SEVERE_SYMPTOMS_SLOT: value}

    def validate_has_fever(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_daily_ci__acknowledge_fever")
            dispatcher.utter_message(template="utter_daily_ci__take_acetaminophen")
            dispatcher.utter_message(template="utter_daily_ci__avoid_ibuprofen")
        else:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__acknowledge_no_fever"
            )

        return {HAS_FEVER_SLOT: value}

    def validate_has_diff_breathing(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value == False:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__acknowledge_no_diff_breathing"
            )

        return {HAS_DIFF_BREATHING_SLOT: value}

    def validate_daily_ci__feel_worse__has_diff_breathing_worsened(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__diff_breathing_worsened_recommendation_1"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__diff_breathing_worsened_recommendation_2"
            )
        else:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__diff_breathing_not_worsened_recommendation_1"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__diff_breathing_not_worsened_recommendation_2"
            )

        return {HAS_DIFF_BREATHING_WORSENED_SLOT: value}

    def validate_has_cough(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_daily_ci__cough_syrup_may_help")
            dispatcher.utter_message(template="utter_daily_ci__cough_syrup_pharmacist")
        else:
            dispatcher.utter_message(template="utter_daily_ci__acknowledge_no_cough")
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__no_cough_recommendation"
            )

        return {HAS_COUGH_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return submit_daily_ci_assessment(tracker)
