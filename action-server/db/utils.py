import logging

import pytz

from .assessment import Assessment
from .reminder import Reminder

logger = logging.getLogger(__name__)

### Sample usage of a sqlalchemy session and the methods provided here.
### Reference: https://docs.sqlalchemy.org/en/13/orm/session_basics.html
#
# from db.base import session_factory
#
# session = session_factory()
#
# try:
#     reminder = create_reminder(session, "America/Toronto", {"metadata": "value"})
#     session.flush()
#
#     assessment = create_assessment(session, reminder.id, {"metadata": "other value"})
#
#     session.commit()
#     session.close()
#     # All changes are commited, great!
# except:
#     session.rollback()
#     # Something wrong happened, but *nothing* was actually commited.
#


def create_reminder(session, timezone, attributes):
    try:
        timezone = pytz.timezone(timezone).zone
    except:
        logger.exception(
            "Could not instantiate timezone with name '%s'. Reminder will be created without specifying timezone.",
            timezone,
        )
        timezone = None

    reminder = Reminder(timezone, attributes)
    session.add(reminder)
    return reminder


def create_assessment(session, reminder_id, attributes):
    assessment = Assessment(reminder_id, attributes)
    session.add(assessment)
    return assessment
