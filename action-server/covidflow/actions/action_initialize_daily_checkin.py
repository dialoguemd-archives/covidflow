import logging
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from .constants import (
    AGE_OVER_65_SLOT,
    FIRST_NAME_SLOT,
    HAS_DIALOGUE_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_SYMPTOMS_SLOT,
    PRECONDITIONS_SLOT,
    PROVINCE_SLOT,
    PROVINCIAL_811_SLOT,
)
from ..lib.hashids_util import create_hashids
from ..lib.provincial_811 import get_provincial_811
from ..db.assessment import Assessment
from ..db.base import session_factory
from ..db.reminder import Reminder

logger = logging.getLogger(__name__)

ACTION_NAME = "action_initialize_daily_checkin"

DEFAULT_SYMPTOMS_VALUE = "moderate"
DEFAULT_FIRST_NAME_VALUE = ""
DEFAULT_PROVINCE_VALUE = None

DEFAULT_REMINDER_VALUES = {
    FIRST_NAME_SLOT: DEFAULT_FIRST_NAME_VALUE,
    PROVINCE_SLOT: DEFAULT_PROVINCE_VALUE,
    AGE_OVER_65_SLOT: False,
    PRECONDITIONS_SLOT: False,
    HAS_DIALOGUE_SLOT: False,
}

DEFAULT_ASSESSMENT_VALUES = {
    LAST_SYMPTOMS_SLOT: DEFAULT_SYMPTOMS_VALUE,
    LAST_HAS_COUGH_SLOT: False,
    LAST_HAS_FEVER_SLOT: False,
    LAST_HAS_DIFF_BREATHING_SLOT: False,
}

METADATA_SLOT = "metadata"
REMINDER_ID_PROPERTY_NAME = "reminder_id"


class ActionInitializeDailyCheckin(Action):
    def __init__(self):
        self.hashids = create_hashids()

    def name(self) -> Text:
        return ACTION_NAME

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        metadata = tracker.get_slot(METADATA_SLOT)
        hashed_id = metadata[REMINDER_ID_PROPERTY_NAME]
        reminder_id = self.hashids.decode(hashed_id)[0]

        session = session_factory()

        user_slots = _get_user_info(session, reminder_id, domain)
        assessment_slots = _get_last_assessment_slots(session, reminder_id)

        session.close()

        return [
            SlotSet(name, value)
            for name, value in {**user_slots, **assessment_slots}.items()
        ]


def _get_user_info(session, reminder_id: str, domain: Dict[Text, Any]) -> dict:
    try:
        reminder = session.query(Reminder).get(reminder_id)
    except:
        reminder = None

    if reminder is None:
        logger.warning(
            f"Reminder with id '{reminder_id}' does not exist. Could not fetch user profile. Filling up with defaults."
        )
        return {
            **DEFAULT_REMINDER_VALUES,
            PROVINCIAL_811_SLOT: get_provincial_811(DEFAULT_PROVINCE_VALUE, domain),
        }

    province = reminder.province
    return {
        FIRST_NAME_SLOT: _fill(reminder.first_name, DEFAULT_FIRST_NAME_VALUE),
        PROVINCE_SLOT: province,
        AGE_OVER_65_SLOT: _fill_false(reminder.age_over_65),
        PRECONDITIONS_SLOT: _fill_false(reminder.preconditions),
        HAS_DIALOGUE_SLOT: _fill_false(reminder.has_dialogue),
        PROVINCIAL_811_SLOT: get_provincial_811(province, domain),
    }


def _get_last_assessment_slots(session, reminder_id: str) -> dict:
    try:
        assessment = (
            session.query(Assessment)
            .filter_by(reminder_id=reminder_id)
            .order_by(Assessment.completed_at.desc())
            .first()
        )
    except:
        assessment = None

    if assessment is None:
        logger.error(
            f"Could not fetch last assessment for reminder id: {reminder_id}. Filling up last assessment values with defaults."
        )
        return DEFAULT_ASSESSMENT_VALUES

    return {
        LAST_SYMPTOMS_SLOT: _fill(assessment.symptoms, DEFAULT_SYMPTOMS_VALUE),
        LAST_HAS_COUGH_SLOT: _fill_false(assessment.has_cough),
        LAST_HAS_FEVER_SLOT: _fill_false(assessment.has_fever),
        LAST_HAS_DIFF_BREATHING_SLOT: _fill_false(assessment.has_diff_breathing),
    }


def _fill(value, default_value):
    return value if value is not None else default_value


def _fill_false(value):
    return _fill(value, False)
