from typing import Any, Dict, Text

import structlog

from covidflow.db.assessment import Assessment
from covidflow.db.base import session_factory
from covidflow.db.reminder import Reminder

from .hashids_util import decode_reminder_id, encode_reminder_id
from .phone_number_validation import is_test_phone_number

logger = structlog.get_logger()

PHONE_NUMBER_SLOT = "phone_number"
METADATA_SLOT = "metadata"
REMINDER_ID_METADATA_PROPERTY = "reminder_id"


def ci_enroll(slot_values: Dict[Text, Any]):
    session = session_factory()
    try:
        if _is_test_session(session, slot_values):
            return

        reminder = _save_reminder(session, slot_values)
        session.flush()
        assessment = _save_assessment(session, slot_values, reminder.id)

        session.commit()

        hashed_id = encode_reminder_id(reminder.id)
        logger.info("Saved reminder to database", hashed_id=hashed_id)
        logger.debug("Saved assessment to database", assessment=assessment)
    except:
        session.rollback()
        raise
    finally:
        session.close()


def cancel_reminder(slot_values: Dict[Text, Any]):
    session = session_factory()
    try:
        if _is_test_session(session, slot_values):
            return

        reminder_id = _get_reminder_id(slot_values)
        reminder = session.query(Reminder).get(reminder_id)
        reminder.is_canceled = True

        session.commit()

        logger.debug("Canceled reminder", reminder=reminder)
    except:
        session.rollback()
        raise
    finally:
        session.close()


def save_assessment(slot_values: Dict[Text, Any], reminder_id=None):
    logger.debug("Saving assessment")

    session = session_factory()
    try:
        if _is_test_session(session, slot_values):
            return

        reminder_id = reminder_id or _get_reminder_id(slot_values)
        assessment = _save_assessment(session, slot_values, reminder_id)

        session.commit()

        logger.debug("Saved assessment", assessment=assessment)
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_reminder(slot_values: Dict[Text, Any]) -> Reminder:
    logger.debug("Fetching reminder")

    session = session_factory()
    try:
        reminder_id = _get_reminder_id(slot_values)
        reminder = session.query(Reminder).get(reminder_id)
        if reminder is None:
            raise Exception("Reminder does not exist")

    except:
        raise
    finally:
        session.close()

    return reminder


def get_last_assessment(slot_values: Dict[Text, Any]) -> Assessment:
    logger.debug("Fetching last assessment")

    session = session_factory()
    try:

        reminder_id = _get_reminder_id(slot_values)
        assessment = (
            session.query(Assessment)
            .filter_by(reminder_id=reminder_id)
            .order_by(Assessment.completed_at.desc())
            .first()
        )
        if assessment is None:
            raise Exception("There are no assessments linked to this reminder")

    except:
        raise
    finally:
        session.close()

    return assessment


def _save_reminder(session, slot_values: Dict[Text, Any]):
    reminder = Reminder.create_from_slot_values(slot_values)
    session.add(reminder)
    return reminder


def _save_assessment(session, slot_values: Dict[Text, Any], reminder_id):
    assessment = Assessment.create_from_slot_values(reminder_id, slot_values)
    session.add(assessment)
    return assessment


def _get_reminder_id(slot_values: Dict[Text, Any]) -> int:
    metadata = slot_values[METADATA_SLOT]
    hashed_id = metadata[REMINDER_ID_METADATA_PROPERTY]
    return decode_reminder_id(hashed_id)


def _is_test_session(session, slot_values: Dict[Text, Any]) -> bool:
    phone_number = slot_values.get(PHONE_NUMBER_SLOT)

    if phone_number:
        return is_test_phone_number(phone_number)

    reminder_id = _get_reminder_id(slot_values)
    if reminder_id:
        reminder = session.query(Reminder).get(reminder_id)
        return is_test_phone_number(reminder.phone_number)

    return False
