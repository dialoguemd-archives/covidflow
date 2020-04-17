import re
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

FIRST_NAME_SLOT = "first_name"
CONTACT_MODE = "contact_mode"
PHONE_NUMBER_SLOT = "phone_number"
EMAIL_SLOT = "email"
AGE_GROUP_SLOT = "age_group"
PRE_EXISTING_CONDITIONS_SLOT = "pre_existing_conditions"
CHECKIN_TIME_SLOT = "checkin_time"

EMAIL_REGEX = re.compile(r"\S+@\S+\.\S+")
NOT_DIGIT_REGEX = re.compile(r"\D")


class DailyCiEnrollForm(FormAction):
    def name(self) -> Text:

        return "daily_ci_enroll_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        slots = [FIRST_NAME_SLOT, CONTACT_MODE]

        contact_mode = tracker.get_slot(CONTACT_MODE)

        if contact_mode == "phone":
            slots.append(PHONE_NUMBER_SLOT)
        elif contact_mode == "email":
            slots.append(EMAIL_SLOT)

        slots += [AGE_GROUP_SLOT, PRE_EXISTING_CONDITIONS_SLOT, CHECKIN_TIME_SLOT]

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            FIRST_NAME_SLOT: self.from_text(),
            PHONE_NUMBER_SLOT: self.from_text(),
            EMAIL_SLOT: self.from_text(),
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
        dispatcher.utter_message(template="utter_thanks_first_name", first_name=value)

        return {FIRST_NAME_SLOT: value}

    def validate_phone_number(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        phone_number = _get_phone_number(value)

        return {PHONE_NUMBER_SLOT: phone_number}

    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        email = _get_email(value)

        return {EMAIL_SLOT: email}

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

        dispatcher.utter_message(template="utter_daily_ci_enroll_done")
        dispatcher.utter_message(template="utter_daily_ci_enroll_follow_up")

        return slot_values

    def validate_checkin_time(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        dispatcher.utter_message(template=f"utter_acknowledge_checkin_time_{value}")

        return {CHECKIN_TIME_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return []


def _get_email(text: Text) -> Optional[Text]:
    match = EMAIL_REGEX.search(text)

    return match.group() if match else None


def _get_phone_number(text: Text) -> Optional[Text]:
    digits = NOT_DIGIT_REGEX.sub("", text)
    valid_length = len(digits) == 10 or len(digits) == 11

    return digits if valid_length else None
