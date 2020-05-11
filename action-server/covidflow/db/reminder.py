import copy
from datetime import datetime, timedelta
from typing import Any, Dict, Text

import pytz
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    Time,
    case,
    cast,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from structlog import get_logger

from db.base import Base

logger = get_logger(__name__)


FIRST_NAME_ATTRIBUTE = "first_name"
PHONE_NUMBER_ATTRIBUTE = "phone_number"
LANGUAGE_ATTRIBUTE = "language"
PROVINCE_ATTRIBUTE = "province"
AGE_OVER_65_ATTRIBUTE = "age_over_65"
PRECONDITIONS_ATTRIBUTE = "preconditions"
HAS_DIALOGUE_ATTRIBUTE = "has_dialogue"

FIRST_NAME_SLOT = "first_name"
PHONE_NUMBER_SLOT = "phone_number"
LANGUAGE_SLOT = "language"
PROVINCE_SLOT = "province"
AGE_OVER_65_SLOT = "age_over_65"
PRECONDITIONS_SLOT = "preconditions"
HAS_DIALOGUE_SLOT = "has_dialogue"
METADATA_SLOT = "metadata"
TIMEZONE_METADATA_PROPERTY = "timezone"

SLOT_MAPPING = {
    FIRST_NAME_SLOT: FIRST_NAME_ATTRIBUTE,
    PHONE_NUMBER_SLOT: PHONE_NUMBER_ATTRIBUTE,
    LANGUAGE_SLOT: LANGUAGE_ATTRIBUTE,
    PROVINCE_SLOT: PROVINCE_ATTRIBUTE,
    AGE_OVER_65_SLOT: AGE_OVER_65_ATTRIBUTE,
    PRECONDITIONS_SLOT: PRECONDITIONS_ATTRIBUTE,
    HAS_DIALOGUE_SLOT: HAS_DIALOGUE_ATTRIBUTE,
}

REMINDER_FREQUENCY = timedelta(days=1)


def _uniformize_timezone(timezone):
    if timezone is None:
        return None

    try:
        return pytz.timezone(timezone).zone
    except:
        logger.warning(
            "Could not instantiate timezone. Reminder will be created without specifying timezone.",
            timezone=timezone,
            exc_info=True,
        )
        return None


class Reminder(Base):
    __tablename__ = "reminder"

    id = Column("id", Integer, primary_key=True)
    created_at = Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    last_reminded_at = Column("last_reminded_at", DateTime(timezone=True))
    timezone = Column("timezone", String(), CheckConstraint("is_timezone(timezone)"))
    is_canceled = Column(
        "is_canceled", Boolean(), nullable=False, server_default="false"
    )
    attributes = Column("attributes", JSONB, nullable=False)

    def __init__(
        self,
        timezone=None,
        id=None,
        created_at=None,
        last_reminded_at=None,
        is_canceled=None,
        attributes=dict(),
    ):
        self.id = id
        self.created_at = created_at
        self.last_reminded_at = last_reminded_at
        self.timezone = _uniformize_timezone(timezone)
        self.is_canceled = is_canceled
        self.attributes = copy.deepcopy(attributes)

    @staticmethod
    def create_from_slot_values(slot_values: Dict[Text, Any]):
        metadata = slot_values.get(METADATA_SLOT) or {}
        timezone = metadata.get(TIMEZONE_METADATA_PROPERTY, None)

        reminder = Reminder(timezone)
        for slot_name, attribute_name in SLOT_MAPPING.items():
            reminder._set_attribute(attribute_name, slot_values.get(slot_name, None))

        return reminder

    # For Unit tests
    def __eq__(self, other):
        if not isinstance(other, Reminder):
            return False
        if self.id != other.id:
            return False
        if self.created_at != other.created_at:
            return False
        if self.last_reminded_at != other.last_reminded_at:
            return False
        if self.timezone != other.timezone:
            return False
        if self.is_canceled != other.is_canceled:
            return False
        if self.attributes != other.attributes:
            return False
        return True

    def _set_attribute(self, attribute, value):
        if value is not None:
            self.attributes[attribute] = value

    @hybrid_property
    def next_reminder_due_date(self):
        should_have_been_last_reminded_at = (
            self.created_at
            if self.last_reminded_at is None
            else datetime.combine(self.last_reminded_at.date(), self.created_at.time())
        )
        return should_have_been_last_reminded_at + REMINDER_FREQUENCY

    @next_reminder_due_date.expression  # type: ignore
    def next_reminder_due_date(cls):
        return (
            case(
                [(cls.last_reminded_at == None, cls.created_at)],
                else_=cast(cls.last_reminded_at, Date)
                + cast(cls.created_at, Time(timezone=True)),
            )
            + REMINDER_FREQUENCY
        )

    @property
    def first_name(self):
        return self.attributes.get(FIRST_NAME_ATTRIBUTE)

    @first_name.setter
    def first_name(self, first_name):
        self._set_attribute(FIRST_NAME_ATTRIBUTE, first_name)

    @property
    def phone_number(self):
        return self.attributes.get(PHONE_NUMBER_ATTRIBUTE)

    @phone_number.setter
    def phone_number(self, phone_number):
        self._set_attribute(PHONE_NUMBER_ATTRIBUTE, phone_number)

    @property
    def language(self):
        return self.attributes.get(LANGUAGE_ATTRIBUTE)

    @language.setter
    def language(self, language):
        self._set_attribute(LANGUAGE_ATTRIBUTE, language)

    @property
    def province(self):
        return self.attributes.get(PROVINCE_ATTRIBUTE)

    @province.setter
    def province(self, province):
        self._set_attribute(PROVINCE_ATTRIBUTE, province)

    @property
    def age_over_65(self):
        return self.attributes.get(AGE_OVER_65_ATTRIBUTE)

    @age_over_65.setter
    def age_over_65(self, age_over_65):
        self._set_attribute(AGE_OVER_65_ATTRIBUTE, age_over_65)

    @property
    def preconditions(self):
        return self.attributes.get(PRECONDITIONS_ATTRIBUTE)

    @preconditions.setter
    def preconditions(self, preconditions):
        self._set_attribute(PRECONDITIONS_ATTRIBUTE, preconditions)

    @property
    def has_dialogue(self):
        return self.attributes.get(HAS_DIALOGUE_ATTRIBUTE)

    @has_dialogue.setter
    def has_dialogue(self, has_dialogue):
        self._set_attribute(HAS_DIALOGUE_ATTRIBUTE, has_dialogue)

    def __repr__(self):
        items = ", ".join(
            [f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_")]
        )
        return f"{self.__class__.__name__}({items})"
