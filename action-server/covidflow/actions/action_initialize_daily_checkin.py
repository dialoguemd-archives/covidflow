from typing import Any, Dict, List, Optional, Text

import structlog
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import (
    AGE_OVER_65_SLOT,
    FIRST_NAME_SLOT,
    HAS_DIALOGUE_SLOT,
    INVALID_REMINDER_ID_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    PRECONDITIONS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
    Symptoms,
)
from covidflow.utils.persistence import get_last_assessment, get_reminder

from .lib.log_util import bind_logger
from .lib.provincial_811 import get_provincial_811

logger = structlog.get_logger()

ACTION_NAME = "action_initialize_daily_checkin"

DEFAULT_SYMPTOMS_VALUE = Symptoms.MODERATE
DEFAULT_FIRST_NAME_VALUE = ""
DEFAULT_PROVINCE_VALUE = None

DEFAULT_ASSESSMENT_VALUES = {
    LAST_SYMPTOMS_SLOT: DEFAULT_SYMPTOMS_VALUE,
    LAST_HAS_COUGH_SLOT: False,
    LAST_HAS_FEVER_SLOT: False,
    LAST_HAS_DIFF_BREATHING_SLOT: False,
}


class ActionInitializeDailyCheckin(Action):
    def name(self) -> Text:
        return ACTION_NAME

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        current_slot_values = tracker.current_slot_values()

        user_slots = _get_user_info(current_slot_values, domain)
        if user_slots is None:
            dispatcher.utter_message(
                template="utter_daily_ci__invalid_id__invalid_link"
            )
            dispatcher.utter_message(template="utter_daily_ci__invalid_id__try_again")
            return [SlotSet(INVALID_REMINDER_ID_SLOT, True)]

        assessment_slots = _get_last_assessment_slots(current_slot_values)

        return [
            SlotSet(name, value)
            for name, value in {**user_slots, **assessment_slots}.items()
        ]


def _get_user_info(
    current_slot_values: Dict[Text, Any], domain: Dict[Text, Any]
) -> Optional[dict]:
    try:
        reminder = get_reminder(current_slot_values)
    except:
        logger.warning(f"Could not fetch user profile. Encoded ID is invalid.")
        return None

    province = reminder.province
    return {
        FIRST_NAME_SLOT: _fill(reminder.first_name, DEFAULT_FIRST_NAME_VALUE),
        PROVINCE_SLOT: province,
        AGE_OVER_65_SLOT: _fill_false(reminder.age_over_65),
        PRECONDITIONS_SLOT: _fill_false(reminder.preconditions),
        HAS_DIALOGUE_SLOT: _fill_false(reminder.has_dialogue),
        PROVINCIAL_811_SLOT: get_provincial_811(province, domain),
    }


def _get_last_assessment_slots(current_slot_values: Dict[Text, Any]) -> dict:
    try:
        assessment = get_last_assessment(current_slot_values)
    except:
        logger.error(
            f"Could not fetch last assessment. Filling up last assessment values with defaults."
        )
        return DEFAULT_ASSESSMENT_VALUES

    return {
        LAST_SYMPTOMS_SLOT: _fill_symptoms(assessment.symptoms),
        LAST_HAS_COUGH_SLOT: _fill_false(assessment.has_cough),
        LAST_HAS_FEVER_SLOT: _fill_false(assessment.has_fever),
        LAST_HAS_DIFF_BREATHING_SLOT: _fill_false(assessment.has_diff_breathing),
    }


def _fill(value, default_value):
    return value if value is not None else default_value


def _fill_false(value):
    return _fill(value, False)


def _fill_symptoms(value):
    if value is None:
        return DEFAULT_SYMPTOMS_VALUE

    # Safety net - dialogue only support MODERATE and MILD symptoms
    if value not in [Symptoms.MODERATE, Symptoms.MILD]:
        new_value = Symptoms.MILD if value == Symptoms.NONE else DEFAULT_SYMPTOMS_VALUE
        logger.warning(
            f"Invalid {LAST_SYMPTOMS_SLOT} value: '{value}' - will continue with '{new_value}'"
        )
        return new_value

    return value
