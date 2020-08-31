import re
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from covidflow.constants import (
    FIRST_NAME_SLOT,
    HAS_DIALOGUE_SLOT,
    LANGUAGE_SLOT,
    PHONE_NUMBER_SLOT,
    PRECONDITIONS_SLOT,
)
from covidflow.utils.persistence import ci_enroll
from covidflow.utils.phone_number_validation import (
    VALIDATION_CODE_LENGTH,
    send_validation_code,
)

from .lib.form_helper import (
    request_next_slot,
    validate_boolean_slot,
    yes_no_nlu_mapping,
)
from .lib.log_util import bind_logger

FORM_NAME = "daily_ci_enroll_form"

DO_ENROLL_SLOT = "daily_ci_enroll__do_enroll"
PHONE_TRY_COUNTER_SLOT = "daily_ci_enroll__phone_number_error_counter"
PHONE_TO_CHANGE_SLOT = "daily_ci_enroll__phone_number_to_change"
VALIDATION_CODE_SLOT = "daily_ci_enroll__validation_code"
VALIDATION_CODE_REFERENCE_SLOT = "daily_ci_enroll__validation_code_reference"
CODE_TRY_COUNTER_SLOT = "daily_ci_enroll__validation_code_error_counter"
NO_CODE_SOLUTION_SLOT = "daily_ci_enroll__no_code_solution"
JUST_SENT_CODE_SLOT = "daily_ci_enroll__just_sent_code"
WANTS_CANCEL_SLOT = "daily_ci_enroll__wants_cancel"
PRECONDITIONS_WITH_EXAMPLES_SLOT = "daily_ci_enroll__preconditions_examples"

PHONE_TRY_MAX = 2
CODE_TRY_MAX = 2

NOT_DIGIT_REGEX = re.compile(r"\D")


class DailyCiEnrollForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

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
            return [
                SlotSet(PRECONDITIONS_WITH_EXAMPLES_SLOT, "N/A")
            ] + await super()._activate_if_required(dispatcher, tracker, domain)

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if tracker.get_slot(DO_ENROLL_SLOT):
            slots = [
                DO_ENROLL_SLOT,
                FIRST_NAME_SLOT,
                WANTS_CANCEL_SLOT,
                PHONE_NUMBER_SLOT,
                NO_CODE_SOLUTION_SLOT,
                VALIDATION_CODE_SLOT,
                PRECONDITIONS_WITH_EXAMPLES_SLOT,
                PRECONDITIONS_SLOT,
                HAS_DIALOGUE_SLOT,
            ]
        else:
            slots = [DO_ENROLL_SLOT]

        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            DO_ENROLL_SLOT: yes_no_nlu_mapping(self),
            FIRST_NAME_SLOT: self.from_text(),
            PHONE_NUMBER_SLOT: [
                self.from_intent(intent="no_phone", value="no_phone"),
                self.from_intent(intent="cancel", value="cancel"),
                self.from_text(),
            ],
            WANTS_CANCEL_SLOT: [self.from_intent(intent="cancel", value=True)]
            + yes_no_nlu_mapping(self),
            VALIDATION_CODE_SLOT: [
                self.from_intent(intent="did_not_get_code", value="did_not_get_code"),
                self.from_intent(intent="change_phone", value="change_phone"),
                self.from_text(),
            ],
            NO_CODE_SOLUTION_SLOT: [
                self.from_intent(intent="new_code", value="new_code"),
                self.from_intent(intent="change_phone", value="change_phone"),
                self.from_text(),
            ],
            PRECONDITIONS_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
                self.from_intent(intent="dont_know", value="need_examples"),
                self.from_intent(intent="help_preconditions", value="need_examples"),
                self.from_text(),
            ],
            PRECONDITIONS_WITH_EXAMPLES_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
                self.from_intent(intent="dont_know", value="dont_know"),
                self.from_text(),
            ],
            HAS_DIALOGUE_SLOT: yes_no_nlu_mapping(self),
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
        if slot == PHONE_NUMBER_SLOT and tracker.get_slot(PHONE_TO_CHANGE_SLOT) is True:
            return "utter_ask_phone_number_new"

        if slot == PHONE_NUMBER_SLOT and tracker.get_slot(PHONE_TRY_COUNTER_SLOT) > 0:
            return "utter_ask_phone_number_error"

        if (
            slot == VALIDATION_CODE_SLOT
            # The message after a send or re-send should never be an error message
            and not (tracker.get_slot(JUST_SENT_CODE_SLOT) is True)
        ):
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
        slots = {PHONE_TO_CHANGE_SLOT: False}
        if value == "no_phone":
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__no_phone_no_checkin"
            )
            dispatcher.utter_message(template="utter_daily_ci_enroll__continue")

            return {**slots, PHONE_NUMBER_SLOT: None, DO_ENROLL_SLOT: False}

        if value == "cancel":
            return {**slots, PHONE_NUMBER_SLOT: None, WANTS_CANCEL_SLOT: None}

        phone_number = _get_phone_number(value)

        if phone_number is not None:
            dispatcher.utter_message(template="utter_daily_ci_enroll__acknowledge")

            return {
                PHONE_NUMBER_SLOT: phone_number,
                **slots,
                **await _send_validation_code(tracker, dispatcher, phone_number),
            }

        try_counter = tracker.get_slot(PHONE_TRY_COUNTER_SLOT)
        if try_counter == PHONE_TRY_MAX:
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__invalid_phone_no_checkin"
            )
            return {**slots, PHONE_NUMBER_SLOT: None, DO_ENROLL_SLOT: False}

        dispatcher.utter_message(template="utter_daily_ci_enroll__invalid_phone_number")

        return {
            **slots,
            PHONE_NUMBER_SLOT: None,
            PHONE_TRY_COUNTER_SLOT: try_counter + 1,
        }

    @validate_boolean_slot
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

    async def validate_daily_ci_enroll__validation_code(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        # User corrects phone number
        phone_number_in_message = _get_phone_number(
            tracker.latest_message.get("text", "")
        )
        if phone_number_in_message is not None:
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__acknowledge_new_phone_number"
            )
            return {
                VALIDATION_CODE_SLOT: None,
                PHONE_NUMBER_SLOT: phone_number_in_message,
                PHONE_TO_CHANGE_SLOT: False,
                **await _send_validation_code(
                    tracker, dispatcher, phone_number_in_message
                ),
            }

        if value == "change_phone":
            return {
                VALIDATION_CODE_SLOT: None,
                PHONE_NUMBER_SLOT: None,
                PHONE_TO_CHANGE_SLOT: True,
            }

        if value == "did_not_get_code":
            error_result = _check_code_error_counter(tracker, dispatcher)
            return {
                **error_result,
                NO_CODE_SOLUTION_SLOT: None,
            }

        validation_code = _get_validation_code(value)
        if validation_code == tracker.get_slot(VALIDATION_CODE_REFERENCE_SLOT):
            dispatcher.utter_message(template="utter_daily_ci_enroll__thanks")
            return {
                VALIDATION_CODE_SLOT: validation_code,
                JUST_SENT_CODE_SLOT: False,
            }

        return _check_code_error_counter(tracker, dispatcher)

    async def validate_daily_ci_enroll__no_code_solution(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        slots = {NO_CODE_SOLUTION_SLOT: value}
        if value == "change_phone":
            return {**slots, PHONE_NUMBER_SLOT: None, PHONE_TO_CHANGE_SLOT: True}

        if value == "new_code":
            return {**slots, **await _send_validation_code(tracker, dispatcher)}

        return {NO_CODE_SOLUTION_SLOT: None}

    def validate_preconditions(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if isinstance(value, bool):
            dispatcher.utter_message(template="utter_daily_ci_enroll__acknowledge")
            return {PRECONDITIONS_SLOT: value}

        if value == "need_examples":
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__explain_preconditions"
            )

            return {PRECONDITIONS_SLOT: None, PRECONDITIONS_WITH_EXAMPLES_SLOT: None}
        else:
            return {PRECONDITIONS_SLOT: None}

    async def validate_daily_ci_enroll__preconditions_examples(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if isinstance(value, bool):
            dispatcher.utter_message(template="utter_daily_ci_enroll__acknowledge")
            return {PRECONDITIONS_WITH_EXAMPLES_SLOT: value, PRECONDITIONS_SLOT: value}

        if value == "dont_know":
            dispatcher.utter_message(
                template="utter_daily_ci_enroll__note_preconditions"
            )

            return {PRECONDITIONS_WITH_EXAMPLES_SLOT: value, PRECONDITIONS_SLOT: True}
        else:
            return {PRECONDITIONS_WITH_EXAMPLES_SLOT: None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot(DO_ENROLL_SLOT) is True:
            try:
                ci_enroll(tracker.current_slot_values())

                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__enroll_done_1"
                )
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__enroll_done_2"
                )
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__enroll_done_3"
                )
            except:
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__enroll_fail_1"
                )
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__enroll_fail_2"
                )
                dispatcher.utter_message(
                    template="utter_daily_ci_enroll__enroll_fail_3"
                )

        return []


def _get_first_name(text: Text) -> Optional[Text]:
    first_name = text.rstrip()

    return first_name if first_name else None


def _get_phone_number(text: Text) -> Optional[Text]:
    digits = NOT_DIGIT_REGEX.sub("", text)
    if len(digits) == 11 and digits[0] == "1":
        return digits
    if len(digits) == 10:
        return f"1{digits}"

    return None


def _get_validation_code(text: Text) -> Optional[Text]:
    digits = NOT_DIGIT_REGEX.sub("", text)
    valid_length = len(digits) == VALIDATION_CODE_LENGTH

    return digits if valid_length else None


async def _send_validation_code(
    tracker: Tracker,
    dispatcher: CollectingDispatcher,
    phone_number: Optional[str] = None,
) -> Dict[Text, Any]:
    if phone_number is None:
        phone_number = tracker.get_slot(PHONE_NUMBER_SLOT)

    first_name = tracker.get_slot(FIRST_NAME_SLOT)
    language = tracker.get_slot(LANGUAGE_SLOT)

    validation_code = await send_validation_code(phone_number, language, first_name)
    if validation_code is None:
        dispatcher.utter_message(
            template="utter_daily_ci_enroll__validation_code_not_sent_1"
        )
        dispatcher.utter_message(
            template="utter_daily_ci_enroll__validation_code_not_sent_2"
        )
        dispatcher.utter_message(template="utter_daily_ci_enroll__continue")

        return {DO_ENROLL_SLOT: False}

    return {VALIDATION_CODE_REFERENCE_SLOT: validation_code, JUST_SENT_CODE_SLOT: True}


def _check_code_error_counter(
    tracker: Tracker, dispatcher: CollectingDispatcher
) -> Dict[Text, Any]:
    try_counter = tracker.get_slot(CODE_TRY_COUNTER_SLOT)

    if try_counter == CODE_TRY_MAX:
        dispatcher.utter_message(
            template="utter_daily_ci_enroll__invalid_phone_no_checkin"
        )
        return {VALIDATION_CODE_SLOT: None, DO_ENROLL_SLOT: False}

    return {
        VALIDATION_CODE_SLOT: None,
        CODE_TRY_COUNTER_SLOT: try_counter + 1,
        JUST_SENT_CODE_SLOT: False,
    }
