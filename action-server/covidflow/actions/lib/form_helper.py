from typing import Any, Callable, Dict, List, Optional, Text, Union

import structlog
from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

from covidflow.constants import SKIP_SLOT_PLACEHOLDER

logger = structlog.get_logger()


VALIDATION_FUNCTION_PREFIX = "validate_"


def request_next_slot(
    form: FormAction,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
    utter_ask_slot_template: Optional[Callable[[str, Tracker], Optional[str]]] = None,
) -> Optional[List[EventType]]:
    """Request the next slot and utter template if needed,
        else return None.
        If requested doesn't change (we didn't get a valid answer), plays error message if present in domain
        This behaviour is overridable with utter_ask_slot_template parameter
        """

    for slot in form.required_slots(tracker):
        if form._should_request_slot(tracker, slot):
            logger.debug(f"Request next slot '{slot}'")

            template = (
                utter_ask_slot_template(slot, tracker)
                if utter_ask_slot_template
                else None
            )

            if template is None:
                if tracker.get_slot(REQUESTED_SLOT) == slot and _has_template(
                    domain, f"utter_ask_{slot}_error"
                ):
                    template = f"utter_ask_{slot}_error"
                else:
                    template = f"utter_ask_{slot}"

            dispatcher.utter_message(template=template, **tracker.slots)

            return [SlotSet(REQUESTED_SLOT, slot)]

    # no more required slots to fill
    return None


def yes_no_nlu_mapping(form: FormAction) -> List[Dict]:
    return [
        form.from_intent(intent="affirm", value=True),
        form.from_intent(intent="deny", value=False),
        form.from_text(),
    ]


def validate_boolean_slot(validator):
    def new_validator(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if not isinstance(value, bool):
            slot_name = validator.__name__[len(VALIDATION_FUNCTION_PREFIX) :]
            return {slot_name: None}

        return validator(self, value, dispatcher, tracker, domain)

    new_validator.__name__ = validator.__name__
    return new_validator


def _has_template(domain: Dict[Text, Any], template: str) -> bool:
    return template in domain.get("responses", {})


def _form_slots_to_validate(tracker: Tracker) -> Dict[Text, Any]:
    """
    Waiting for a solution to: https://github.com/RasaHQ/rasa-sdk/issues/269
    I copied the function and adapted it and replaced it where it does change something.
    Get form slots which need validation.
    You can use a custom action to validate slots which were extracted during the
    latest form execution. This method provides you all extracted candidates for
    form slots.
    Returns:
        A mapping of extracted slot candidates and their values.
    """

    slots_to_validate = {}

    # Thing I changed
    # if not self.active_loop:
    #     return slots_to_validate

    for event in reversed(tracker.events):
        # The `FormAction` in Rasa Open Source will append all slot candidates
        # at the end of the tracker events.
        if event["event"] == "slot":
            slots_to_validate[event["name"]] = event["value"]
        else:
            # Stop as soon as there is another event type as this means that we
            # checked all potential slot candidates.
            break

    return slots_to_validate


# Fills all the slots that were not yet asked. Workaround for https://github.com/RasaHQ/rasa/issues/6569
def end_form_additional_events(
    actual_slot: str, ordered_form_slots: List[str]
) -> List[EventType]:
    actual_slot_index = ordered_form_slots.index(actual_slot)
    return [
        SlotSet(slot, SKIP_SLOT_PLACEHOLDER)
        for slot in ordered_form_slots[actual_slot_index + 1 :]
    ]
