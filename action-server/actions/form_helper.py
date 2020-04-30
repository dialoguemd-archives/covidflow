import logging
from typing import Any, Callable, Dict, List, Optional, Text

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

logger = logging.getLogger(__name__)


def request_next_slot(
    form: FormAction,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
    utter_ask_slot_template: Callable[[str, Tracker], Optional[str]],
) -> Optional[List[EventType]]:
    """Request the next slot and utter template if needed,
        else return None"""

    for slot in form.required_slots(tracker):
        if form._should_request_slot(tracker, slot):
            logger.debug(f"Request next slot '{slot}'")

            template = utter_ask_slot_template(slot, tracker)

            if template is None:
                template = f"utter_ask_{slot}"

            dispatcher.utter_message(template=template, **tracker.slots)

            return [SlotSet(REQUESTED_SLOT, slot)]

    # no more required slots to fill
    return None
