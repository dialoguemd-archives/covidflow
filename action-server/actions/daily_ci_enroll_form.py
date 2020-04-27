import re
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

FORM_NAME = "daily_ci_enroll_form"

FIRST_NAME_SLOT = "first_name"
PHONE_NUMBER_SLOT = "phone_number"
PRE_EXISTING_CONDITIONS_SLOT = "pre_existing_conditions"

NOT_DIGIT_REGEX = re.compile(r"\D")


class DailyCiEnrollForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        slots = [
            FIRST_NAME_SLOT,
            PHONE_NUMBER_SLOT,
            PRE_EXISTING_CONDITIONS_SLOT,
        ]

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            FIRST_NAME_SLOT: self.from_text(),
            PHONE_NUMBER_SLOT: self.from_text(),
            PRE_EXISTING_CONDITIONS_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
                self.from_intent(intent="dont_know", value="dont_know"),
            ],
        }

    def validate_first_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        first_name = _get_first_name(value)

        if first_name:
            dispatcher.utter_message(
                template="utter_thanks_first_name", first_name=first_name
            )
            dispatcher.utter_message(template="utter_text_message_checkin")

        return {FIRST_NAME_SLOT: first_name}

    def validate_phone_number(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        phone_number = _get_phone_number(value)

        if phone_number is not None:
            dispatcher.utter_message(template="utter_acknowledge")

        return {PHONE_NUMBER_SLOT: phone_number}

    def validate_pre_existing_conditions(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        slot_values = {PRE_EXISTING_CONDITIONS_SLOT: value}

        if value == "dont_know":
            dispatcher.utter_message(template="utter_note_pre_existing_conditions")

            slot_values[PRE_EXISTING_CONDITIONS_SLOT] = True

        return slot_values

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        dispatcher.utter_message(template="utter_daily_ci_answers_recorded")
        dispatcher.utter_message(template="utter_daily_ci_enroll_done")
        dispatcher.utter_message(template="utter_daily_ci_enroll_follow_up")

        return []


def _get_first_name(text: Text) -> Optional[Text]:
    first_name = text.rstrip()

    return first_name if first_name else None


def _get_phone_number(text: Text) -> Optional[Text]:
    digits = NOT_DIGIT_REGEX.sub("", text)
    valid_length = len(digits) == 10 or len(digits) == 11

    return digits if valid_length else None
