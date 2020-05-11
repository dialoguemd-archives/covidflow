import copy
import logging
from typing import Any, Dict, Text

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

logger = logging.getLogger(__name__)

SYMPTOMS_SLOT = "symptoms"
HAS_FEVER_SLOT = "has_fever"
HAS_COUGH_SLOT = "has_cough"
HAS_DIFF_BREATHING_SLOT = "has_diff_breathing"
FEEL_WORSE_SLOT = "feel_worse"

SYMPTOMS_ATTRIBUTE = "symptoms"
HAS_FEVER_ATTRIBUTE = "has_fever"
HAS_COUGH_ATTRIBUTE = "has_cough"
HAS_DIFF_BREATHING_ATTRIBUTE = "has_diff_breathing"
FEEL_WORSE_ATTRIBUTE = "feel_worse"

SLOT_MAPPING = {
    SYMPTOMS_SLOT: SYMPTOMS_ATTRIBUTE,
    HAS_FEVER_SLOT: HAS_FEVER_ATTRIBUTE,
    HAS_COUGH_SLOT: HAS_COUGH_ATTRIBUTE,
    HAS_DIFF_BREATHING_SLOT: HAS_DIFF_BREATHING_ATTRIBUTE,
    FEEL_WORSE_SLOT: FEEL_WORSE_ATTRIBUTE,
}

# TODO: We might want to use auto-mapping instead of re-defining the actual tables.
class Assessment(Base):
    __tablename__ = "assessment"

    id = Column("id", Integer, primary_key=True)
    reminder_id = Column(
        "reminder_id",
        Integer,
        ForeignKey("reminder.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    completed_at = Column(
        "completed_at",
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    attributes = Column("attributes", JSONB, nullable=False)

    def __init__(self, reminder_id, id=None, completed_at=None, attributes=dict()):
        self.reminder_id = reminder_id
        self.id = id
        self.completed_at = completed_at
        self.attributes = copy.deepcopy(attributes)

    # For Unit tests
    def __eq__(self, other):
        if not isinstance(other, Assessment):
            return False
        if self.id != other.id:
            return False
        if self.reminder_id != other.reminder_id:
            return False
        if self.completed_at != other.completed_at:
            return False
        if self.attributes != other.attributes:
            return False
        return True

    @staticmethod
    def create_from_slot_values(reminder_id: int, slot_values: Dict[Text, Any]):
        assessment = Assessment(reminder_id)
        for slot_name, attribute_name in SLOT_MAPPING.items():
            assessment._set_attribute(attribute_name, slot_values.get(slot_name, None))

        return assessment

    def _set_attribute(self, attribute, value):
        if value is not None:
            self.attributes[attribute] = value

    @property
    def symptoms(self):
        return self.attributes.get(SYMPTOMS_ATTRIBUTE)

    @symptoms.setter
    def symptoms(self, symptoms):
        self._set_attribute(SYMPTOMS_ATTRIBUTE, symptoms)

    @property
    def has_fever(self):
        return self.attributes.get(HAS_FEVER_ATTRIBUTE)

    @has_fever.setter
    def has_fever(self, has_fever):
        self._set_attribute(HAS_FEVER_ATTRIBUTE, has_fever)

    @property
    def has_cough(self):
        return self.attributes.get(HAS_COUGH_ATTRIBUTE)

    @has_cough.setter
    def has_cough(self, has_cough):
        self._set_attribute(HAS_COUGH_ATTRIBUTE, has_cough)

    @property
    def has_diff_breathing(self):
        return self.attributes.get(HAS_DIFF_BREATHING_ATTRIBUTE)

    @has_diff_breathing.setter
    def has_diff_breathing(self, has_diff_breathing):
        self._set_attribute(HAS_DIFF_BREATHING_ATTRIBUTE, has_diff_breathing)

    @property
    def feel_worse(self):
        return self.attributes.get(FEEL_WORSE_ATTRIBUTE)

    @feel_worse.setter
    def feel_worse(self, feel_worse):
        self._set_attribute(FEEL_WORSE_ATTRIBUTE, feel_worse)

    def __repr__(self):
        items = ", ".join(
            [f"{k}={v}" for k, v in self.__dict__.items() if not k.startswith("_")]
        )
        return f"{self.__class__.__name__}({items})"
