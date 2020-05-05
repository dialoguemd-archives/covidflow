from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.form_helper import request_next_slot

FORM_NAME = "daily_ci_feel_no_change_form"

LAST_SYMPTOMS_SLOT = "last_symptoms"
SELF_ASSESS_DONE_SLOT = "self_assess_done"

FEEL_WORSE_SLOT = "feel_worse"
SYMPTOMS_SLOT = "symptoms"
HAS_FEVER_SLOT = "has_fever"
HAS_DIFF_BREATHING_SLOT = "has_diff_breathing"
HAS_COUGH_SLOT = "has_cough"


class DailyCiFeelNoChangeForm(FormAction):
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
            events.append(SlotSet(FEEL_WORSE_SLOT, False))

        return await super()._activate_if_required(dispatcher, tracker, domain) + events

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        slots = [HAS_FEVER_SLOT, HAS_COUGH_SLOT]

        last_symptoms = tracker.get_slot(LAST_SYMPTOMS_SLOT)

        if last_symptoms == "moderate":
            slots.append(HAS_DIFF_BREATHING_SLOT)

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            HAS_FEVER_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            HAS_COUGH_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            HAS_DIFF_BREATHING_SLOT: [
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
            HAS_FEVER_SLOT,
            HAS_DIFF_BREATHING_SLOT,
            HAS_COUGH_SLOT,
        ]:
            return f"utter_ask_daily_ci__feel_no_change__{slot}"

        return None

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
                template="utter_daily_ci__feel_no_change__acknowledge_no_fever"
            )

        return {HAS_FEVER_SLOT: value}

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

        return {HAS_COUGH_SLOT: value}

    def validate_has_diff_breathing(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        slots = {HAS_DIFF_BREATHING_SLOT: value}

        if value is True:
            dispatcher.utter_message(
                template="utter_daily_ci__feel_no_change__acknowledge_diff_breathing"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__feel_no_change__diff_breathing_recommendation"
            )
        else:
            if (
                tracker.get_slot(HAS_FEVER_SLOT) == False
                and tracker.get_slot(HAS_COUGH_SLOT) == False
            ):
                slots[SYMPTOMS_SLOT] = "mild"

            dispatcher.utter_message(
                template="utter_daily_ci__feel_no_change__acknowledge_no_diff_breathing"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__feel_no_change__no_diff_breathing_recommendation"
            )

        return slots

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        last_symptoms = tracker.get_slot(LAST_SYMPTOMS_SLOT)

        if last_symptoms == "mild":
            dispatcher.utter_message(
                template="utter_daily_ci__feel_no_change__mild_last_symptoms_recommendation"
            )

        return [SlotSet(SELF_ASSESS_DONE_SLOT, True)]
