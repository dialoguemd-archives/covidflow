from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

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

    def __init__(self, reminder_id, attributes):
        self.reminder_id = reminder_id
        self.attributes = attributes
