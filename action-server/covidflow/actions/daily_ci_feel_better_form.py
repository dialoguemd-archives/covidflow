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
    LAST_SYMPTOMS_SLOT,
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

FORM_NAME = "daily_ci_feel_better_form"

HAS_OTHER_MILD_SYMPTOMS_SLOT = "daily_ci__feel_better__has_other_mild_symptoms"
IS_SYMPTOM_FREE_SLOT = "daily_ci__feel_better__is_symptom_free"


class DailyCiFeelBetterForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

    ## override to play initial message and set feel_worse slot
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        events = []

        if tracker.active_form.get("name") != FORM_NAME:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_better__acknowledge"
            )

            events.append(SlotSet(FEEL_WORSE_SLOT, False))

        return await super()._activate_if_required(dispatcher, tracker, domain) + events

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        slots = [HAS_FEVER_SLOT, HAS_COUGH_SLOT]

        last_symptoms = tracker.get_slot(LAST_SYMPTOMS_SLOT)

        if last_symptoms == Symptoms.MODERATE:
            slots.append(HAS_DIFF_BREATHING_SLOT)

            if tracker.get_slot(HAS_DIFF_BREATHING_SLOT) is True:
                return slots

        slots.append(HAS_OTHER_MILD_SYMPTOMS_SLOT)

        if (
            tracker.get_slot(HAS_OTHER_MILD_SYMPTOMS_SLOT) is True
            or tracker.get_slot(HAS_FEVER_SLOT) is True
            or tracker.get_slot(HAS_COUGH_SLOT) is True
        ):
            return slots

        return slots + [IS_SYMPTOM_FREE_SLOT]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            HAS_FEVER_SLOT: yes_no_nlu_mapping(self),
            HAS_COUGH_SLOT: yes_no_nlu_mapping(self),
            HAS_DIFF_BREATHING_SLOT: yes_no_nlu_mapping(self),
            HAS_OTHER_MILD_SYMPTOMS_SLOT: yes_no_nlu_mapping(self),
            IS_SYMPTOM_FREE_SLOT: yes_no_nlu_mapping(self),
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
        if slot in [HAS_FEVER_SLOT, HAS_COUGH_SLOT, HAS_DIFF_BREATHING_SLOT]:
            if tracker.get_slot(REQUESTED_SLOT) == slot:
                return f"utter_ask_daily_ci__feel_better__{slot}_error"
            return f"utter_ask_daily_ci__feel_better__{slot}"

        if (
            slot == HAS_OTHER_MILD_SYMPTOMS_SLOT
            and tracker.get_slot(LAST_SYMPTOMS_SLOT) == Symptoms.MODERATE
            and tracker.get_slot(REQUESTED_SLOT) != slot
        ):
            return f"utter_ask_{slot}_with_acknowledge"

        return None

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
                template="utter_daily_ci__feel_better__acknowledge_no_fever"
            )

        return {HAS_FEVER_SLOT: value}

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

        return {HAS_COUGH_SLOT: value}

    @validate_boolean_slot
    def validate_has_diff_breathing(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        slots = {HAS_DIFF_BREATHING_SLOT: value}

        if value is True:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_better__breathing_difficulty_recommendation_1"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__feel_better__breathing_difficulty_recommendation_2"
            )
        else:
            slots[SYMPTOMS_SLOT] = Symptoms.MILD

        return slots

    @validate_boolean_slot
    def validate_daily_ci__feel_better__has_other_mild_symptoms(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if (
            value is True
            or tracker.get_slot(HAS_FEVER_SLOT) is True
            or tracker.get_slot(HAS_COUGH_SLOT) is True
        ):
            dispatcher.utter_message(
                template="utter_daily_ci__feel_better__has_other_mild_symptoms_recommendation"
            )

        return {HAS_OTHER_MILD_SYMPTOMS_SLOT: value}

    @validate_boolean_slot
    def validate_daily_ci__feel_better__is_symptom_free(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        slots = {IS_SYMPTOM_FREE_SLOT: value}

        if value is True:
            slots[SYMPTOMS_SLOT] = Symptoms.NONE
        else:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_better__has_other_mild_symptoms_still_sick_recommendation"
            )

        return slots

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return submit_daily_ci_assessment(tracker)
