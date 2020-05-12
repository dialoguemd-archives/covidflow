"""Initial db setup.

Revision ID: 00001
Revises:
Create Date: 2020-04-21 13:32:44.422928

"""
import structlog
from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.schema import CheckConstraint, ForeignKey
from sqlalchemy.types import Integer, String

from alembic import op

log = structlog.get_logger()

revision = "00001"
down_revision = None
branch_labels = None
depends_on = None

REMINDER_TABLE = "reminder"
ASSESSMENT_TABLE = "assessment"


def upgrade():
    create_reminder_table()
    create_assessment_table()


def create_reminder_table():
    log.info("Creating reminder table.")

    op.execute(
        """CREATE OR REPLACE FUNCTION is_timezone(tz TEXT) RETURNS BOOLEAN as $$
        DECLARE
            date TIMESTAMPTZ;
        BEGIN
            date := now() AT TIME ZONE tz;
            RETURN TRUE;
        EXCEPTION WHEN invalid_parameter_value THEN
            RETURN FALSE;
        END;
        $$ language plpgsql STABLE;"""
    )

    op.create_table(
        REMINDER_TABLE,
        Column("id", Integer, primary_key=True),
        Column(
            "created_at",
            DateTime(timezone=True),
            server_default=func.current_timestamp(),
            nullable=False,
        ),
        Column("last_reminded_at", DateTime(timezone=True),),
        Column("timezone", String(), CheckConstraint("is_timezone(timezone)"),),
        Column("is_canceled", Boolean(), nullable=False, server_default="false"),
        Column("attributes", JSONB, nullable=False),
    )


def create_assessment_table():
    log.info("Creating assessment table.")

    op.create_table(
        ASSESSMENT_TABLE,
        Column("id", Integer, primary_key=True),
        Column(
            "reminder_id",
            Integer,
            ForeignKey("reminder.id", onupdate="CASCADE", ondelete="CASCADE"),
        ),
        Column(
            "completed_at",
            DateTime(timezone=True),
            server_default=func.current_timestamp(),
            nullable=False,
        ),
        Column("attributes", JSONB, nullable=False),
    )


def downgrade():
    op.drop_table(ASSESSMENT_TABLE)
    op.drop_table(REMINDER_TABLE)

    op.execute("DROP FUNCTION is_timezone(tz TEXT)")
