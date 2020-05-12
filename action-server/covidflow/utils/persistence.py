import logging
from typing import Any, Dict, Text

from covidflow.db.assessment import Assessment
from covidflow.db.base import session_factory
from covidflow.db.reminder import Reminder

from .hashids_util import decode_reminder_id, encode_reminder_id
from .phone_number_validation import is_test_phone_number

logger = logging.getLogger(__name__)

METADATA_SLOT = "metadata"
REMINDER_ID_METADATA_PROPERTY = "reminder_id"


def _get_reminder_id(slot_values: Dict[Text, Any]) -> int:
    metadata = slot_values.get(METADATA_SLOT, {})

    if REMINDER_ID_METADATA_PROPERTY not in metadata:
        raise KeyError(f"Missing {REMINDER_ID_METADATA_PROPERTY} in slot values")

    hashed_id = metadata.get(REMINDER_ID_METADATA_PROPERTY, None)
    return decode_reminder_id(hashed_id)


def save_reminder(slot_values: Dict[Text, Any]):
    reminder = Reminder.create_from_slot_values(slot_values)

    if is_test_phone_number(reminder.phone_number):
        logger.info("555 number: not saving reminder to database")
        return True

    session = session_factory()
    try:
        session.add(reminder)
        session.flush()

        assessment = Assessment.create_from_slot_values(reminder.id, slot_values)
        session.add(assessment)

        session.commit()

        # the following is temporary and will allow us to get the hashids of the new reminders in the logs
        hashed_id = encode_reminder_id(reminder.id)
        logger.info(f"Created new reminder (hashed_id={hashed_id}): {reminder}")

        return True
    except:
        logger.exception("Could not save reminder instance")
        session.rollback()
        return False
    finally:
        session.close()


def cancel_reminder(slot_values: Dict[Text, Any]):
    reminder_id = _get_reminder_id(slot_values)

    session = session_factory()
    try:
        reminder = session.query(Reminder).get(reminder_id)
        reminder.is_canceled = True
        session.commit()
    except:
        logger.exception("Could not cancel reminder")
        session.rollback()
    finally:
        session.close()


def save_assessment(slot_values: Dict[Text, Any]):
    metadata = slot_values.get(METADATA_SLOT, {})

    if REMINDER_ID_METADATA_PROPERTY not in metadata:
        raise KeyError(f"Missing {REMINDER_ID_METADATA_PROPERTY} in slot values")

    hashed_id = metadata.get(REMINDER_ID_METADATA_PROPERTY, None)
    reminder_id = decode_reminder_id(hashed_id)

    session = session_factory()
    try:
        session.add(Assessment.create_from_slot_values(reminder_id, slot_values))
        session.commit()
    except:
        logger.exception("Could not save assessment")
        session.rollback()
    finally:
        session.close()
