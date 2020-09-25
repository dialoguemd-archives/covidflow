from typing import Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from structlog import get_logger

from covidflow.constants import (
    LAST_ASSESSMENT_SLOTS,
    SELF_ASSESS_DONE_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)
from covidflow.utils.persistence import cancel_reminder, save_assessment

from .lib.log_util import bind_logger

logger = get_logger(__name__)

LAST_PREFIX = "last_"

ACTION_NAME = "action_submit_daily_ci_assessment"


class ActionSubmitDailyCiAssessment(Action):
    def name(self):
        return ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)
        events = [SlotSet(SELF_ASSESS_DONE_SLOT, True)]

        ## Filling empty slots with previous day values
        slots_to_add = {}
        for last_slot in LAST_ASSESSMENT_SLOTS:
            current_slot = last_slot.replace(LAST_PREFIX, "")
            if tracker.get_slot(current_slot) is None:
                value = tracker.get_slot(last_slot)
                slots_to_add.update({current_slot: value})

        try:
            save_assessment({**tracker.current_slot_values(), **slots_to_add})
        except:
            logger.warn("Failed to save assessment", exc_info=True)

        if tracker.get_slot(SYMPTOMS_SLOT) == Symptoms.SEVERE:
            try:
                cancel_reminder(tracker.current_slot_values())
            except:
                logger.warn("Failed to cancel reminder", exc_info=True)

        return events + [SlotSet(key, value) for key, value in slots_to_add.items()]
