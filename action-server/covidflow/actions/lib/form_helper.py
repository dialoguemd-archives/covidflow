from typing import Any, Callable, Dict, List, Optional, Text, Union

import structlog
from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

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


def get_extracted_slots(tracker: Tracker, form_name: str) -> Dict[Text, Any]:
    def find_form_event() -> Union[int, None]:
        for index in reversed(range(len(tracker.events))):
            if (
                tracker.events[index]["event"] == "action"
                and tracker.events[index]["name"] == form_name
            ):
                return index
        return None

    last_form_event_index = find_form_event()

    if last_form_event_index is None:
        raise Exception(
            f"Could not find action event for form {form_name} in events to fetch extracted slots"
        )
    else:
        return {
            slot_set["name"]: slot_set["value"]
            for slot_set in tracker.events[last_form_event_index + 1 :]
        }
