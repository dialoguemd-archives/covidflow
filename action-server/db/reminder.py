from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

# TODO: We might want to use auto-mapping instead of re-defining the actual tables.


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

    def __init__(self, timezone, attributes):
        self.timezone = timezone
        self.attributes = attributes

    @property
    def first_name(self):
        return self.attributes["first_name"]

    @property
    def phone_number(self):
        return self.attributes["phone_number"]
