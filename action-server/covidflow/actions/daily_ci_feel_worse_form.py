from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

from covidflow.constants import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    SEVERE_SYMPTOMS_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .daily_ci_assessment_common import submit_daily_ci_assessment
from .lib.form_helper import (
    request_next_slot,
    validate_boolean_slot,
    yes_no_nlu_mapping,
)
from .lib.log_util import bind_logger

FORM_NAME = "daily_ci_feel_worse_form"

HAS_DIFF_BREATHING_WORSENED_SLOT = "daily_ci__feel_worse__has_diff_breathing_worsened"


class DailyCiFeelWorseForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

    ## override to set feel_worse slot
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        events = []

        if tracker.active_loop.get("name") != FORM_NAME:
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
            SEVERE_SYMPTOMS_SLOT: yes_no_nlu_mapping(self),
            HAS_FEVER_SLOT: yes_no_nlu_mapping(self),
            HAS_DIFF_BREATHING_SLOT: yes_no_nlu_mapping(self),
            HAS_DIFF_BREATHING_WORSENED_SLOT: yes_no_nlu_mapping(self),
            HAS_COUGH_SLOT: yes_no_nlu_mapping(self),
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
            if tracker.get_slot(REQUESTED_SLOT) == slot:
                return f"utter_ask_daily_ci__feel_worse__{slot}_error"
            return f"utter_ask_daily_ci__feel_worse__{slot}"

        return None

    @validate_boolean_slot
    def validate_severe_symptoms(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            return {SEVERE_SYMPTOMS_SLOT: value, SYMPTOMS_SLOT: Symptoms.SEVERE}

        dispatcher.utter_message(
            template="utter_daily_ci__feel_worse__acknowledge_no_severe_symptoms"
        )
        return {SEVERE_SYMPTOMS_SLOT: value}

    @validate_boolean_slot
    def validate_has_fever(
        self,
        value: Union[bool, Text],
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

    @validate_boolean_slot
    def validate_has_diff_breathing(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value == False:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_worse__acknowledge_no_diff_breathing"
            )

        return {HAS_DIFF_BREATHING_SLOT: value}

    @validate_boolean_slot
    def validate_daily_ci__feel_worse__has_diff_breathing_worsened(
        self,
        value: Union[bool, Text],
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

    @validate_boolean_slot
    def validate_has_cough(
        self,
        value: Union[bool, Text],
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
