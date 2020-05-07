import logging
from typing import Any, Dict, Text

from actions.lib.hashids_util import decode_reminder_id
from db.assessment import Assessment
from db.base import session_factory

logger = logging.getLogger(__name__)

METADATA_SLOT = "metadata"
REMINDER_ID_METADATA_PROPERTY = "reminder_id"


def store_assessment(slot_values: Dict[Text, Any]):
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
