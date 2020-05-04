import re
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.form_helper import request_next_slot
from actions.lib.phone_number_validation import (
    VALIDATION_CODE_LENGTH,
    send_validation_code,
)

FORM_NAME = "daily_ci_enroll_form"

LANGUAGE_SLOT = "language"

DO_ENROLL_SLOT = "daily_ci_enroll__do_enroll"
FIRST_NAME_SLOT = "first_name"
PHONE_NUMBER_SLOT = "phone_number"
PHONE_TRY_COUNTER_SLOT = "daily_ci_enroll__phone_number_error_counter"
VALIDATION_CODE_SLOT = "daily_ci_enroll__validation_code"
VALIDATION_CODE_REFERENCE_SLOT = "daily_ci_enroll__validation_code_reference"
CODE_TRY_COUNTER_SLOT = "daily_ci_enroll__validation_code_error_counter"
PRE_EXISTING_CONDITIONS_SLOT = "preconditions"
HAS_DIALOGUE_SLOT = "has_dialogue"

WANTS_CANCEL_SLOT = "daily_ci_enroll__wants_cancel"

PHONE_TRY_MAX = 2
CODE_TRY_MAX = 2

NOT_DIGIT_REGEX = re.compile(r"\D")


class DailyCiEnrollForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    ## override to play initial message
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_form.get("name") != FORM_NAME:
            dispatcher.utter_message(template="utter_daily_ci_enroll__offer_checkin")
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__explain_checkin_1"
            )
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__explain_checkin_2"
            )

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if tracker.get_slot(DO_ENROLL_SLOT):
            slots = [
                DO_ENROLL_SLOT,
                FIRST_NAME_SLOT,
                WANTS_CANCEL_SLOT,
                PHONE_NUMBER_SLOT,
                VALIDATION_CODE_SLOT,
                PRE_EXISTING_CONDITIONS_SLOT,
                HAS_DIALOGUE_SLOT,
            ]
        else:
            slots = [DO_ENROLL_SLOT]

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            DO_ENROLL_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            FIRST_NAME_SLOT: self.from_text(),
            PHONE_NUMBER_SLOT: [
                self.from_intent(intent="no_phone", value="no_phone"),
                self.from_intent(intent="cancel", value="cancel"),
                self.from_text(),
            ],
            WANTS_CANCEL_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
            VALIDATION_CODE_SLOT: self.from_text(),
            PRE_EXISTING_CONDITIONS_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
                self.from_intent(intent="dont_know", value="dont_know"),
            ],
            HAS_DIALOGUE_SLOT: [
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
        if slot == PHONE_NUMBER_SLOT and tracker.get_slot(PHONE_TRY_COUNTER_SLOT) > 0:
            return "utter_ask_phone_number_error"

        if slot == VALIDATION_CODE_SLOT and tracker.get_slot(CODE_TRY_COUNTER_SLOT) > 0:
            return "utter_ask_daily_ci_enroll__validation_code_error"

        return None

    def validate_daily_ci_enroll__do_enroll(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(template="utter_daily_ci_enroll__start_enroll")

        return {DO_ENROLL_SLOT: value}

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
                template="utter_daily_ci_enroll__thanks_first_name",
                first_name=first_name,
            )
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__text_message_checkin"
            )

        return {FIRST_NAME_SLOT: first_name}

    async def validate_phone_number(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value == "no_phone":
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__no_phone_no_checkin"
            )
            dispatcher.utter_message(template="utter_daily_ci_enroll__continue")

            return {PHONE_NUMBER_SLOT: None, DO_ENROLL_SLOT: False}

        if value == "cancel":
            return {PHONE_NUMBER_SLOT: None, WANTS_CANCEL_SLOT: None}

        phone_number = _get_phone_number(value)

        if phone_number is not None:
            dispatcher.utter_message(template="utter_daily_ci_enroll__acknowledge")

            first_name = tracker.get_slot(FIRST_NAME_SLOT)
            language = tracker.get_slot(LANGUAGE_SLOT)

            validation_code = await send_validation_code(
                phone_number, language, first_name
            )
            if validation_code is None:
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__validation_code_not_sent_1"
                )
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__validation_code_not_sent_2"
                )
                dispatcher.utter_message(template="utter_daily_ci_enroll__continue")
            return {
                PHONE_NUMBER_SLOT: phone_number,
                VALIDATION_CODE_REFERENCE_SLOT: validation_code,
            }

        try_counter = tracker.get_slot(PHONE_TRY_COUNTER_SLOT)
        if try_counter == PHONE_TRY_MAX:
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__invalid_phone_no_checkin"
            )
            return {PHONE_NUMBER_SLOT: None, DO_ENROLL_SLOT: False}

        dispatcher.utter_message(template="utter_daily_ci_enroll__invalid_phone_number")

        return {PHONE_NUMBER_SLOT: None, PHONE_TRY_COUNTER_SLOT: try_counter + 1}

    def validate_daily_ci_enroll__wants_cancel(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if value is True:
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__no_problem_continue"
            )
            return {WANTS_CANCEL_SLOT: value, DO_ENROLL_SLOT: False}

        dispatcher.utter_message(template="utter_daily_ci_enroll__ok_continue")
        return {
            WANTS_CANCEL_SLOT: value,
            PHONE_TRY_COUNTER_SLOT: tracker.get_slot(PHONE_TRY_COUNTER_SLOT) + 1,
        }

    def validate_daily_ci_enroll__validation_code(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        validation_code = _get_validation_code(value)
        if validation_code == tracker.get_slot(VALIDATION_CODE_REFERENCE_SLOT):
            dispatcher.utter_message(template="utter_daily_ci_enroll__thanks")
            return {VALIDATION_CODE_SLOT: validation_code}

        try_counter = tracker.get_slot(CODE_TRY_COUNTER_SLOT)
        if try_counter == CODE_TRY_MAX:
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__invalid_phone_no_checkin"
            )
            return {VALIDATION_CODE_SLOT: None, DO_ENROLL_SLOT: False}

        return {VALIDATION_CODE_SLOT: None, CODE_TRY_COUNTER_SLOT: try_counter + 1}

    def validate_preconditions(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        slot_values = {PRE_EXISTING_CONDITIONS_SLOT: value}

        if value == "dont_know":
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__note_preconditions"
            )

            slot_values[PRE_EXISTING_CONDITIONS_SLOT] = True

        return slot_values

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot(DO_ENROLL_SLOT) is True:
            dispatcher.utter_message(template="utter_daily_ci_enroll__enroll_done_1")
            dispatcher.utter_message(template="utter_daily_ci_enroll__enroll_done_2")
            dispatcher.utter_message(template="utter_daily_ci_enroll__enroll_done_3")

        return []


def _get_first_name(text: Text) -> Optional[Text]:
    first_name = text.rstrip()

    return first_name if first_name else None


def _get_phone_number(text: Text) -> Optional[Text]:
    digits = NOT_DIGIT_REGEX.sub("", text)
    if len(digits) == 11:
        return digits
    if len(digits) == 10:
        return f"1{digits}"

    return None


def _get_validation_code(text: Text) -> Optional[Text]:
    digits = NOT_DIGIT_REGEX.sub("", text)
    valid_length = len(digits) == VALIDATION_CODE_LENGTH

    return digits if valid_length else None
