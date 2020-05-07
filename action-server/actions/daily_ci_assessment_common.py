from typing import List

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet

from actions.constants import LAST_ASSESSMENT_SLOTS, SELF_ASSESS_DONE_SLOT
from actions.lib.persistence import store_assessment

LAST_PREFIX = "last_"


def submit_daily_ci_assessment(tracker: Tracker) -> List[dict]:
    events = [SlotSet(SELF_ASSESS_DONE_SLOT, True)]

    ## Filling empty slots with previous day values
    slots_to_add = {}
    for last_slot in LAST_ASSESSMENT_SLOTS:
        current_slot = last_slot.replace(LAST_PREFIX, "")
        if tracker.get_slot(current_slot) is None:
            value = tracker.get_slot(last_slot)
            slots_to_add.update({current_slot: value})

    store_assessment({**tracker.current_slot_values(), **slots_to_add})

    return events + [SlotSet(key, value) for key, value in slots_to_add.items()]
