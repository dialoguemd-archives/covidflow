"""Initial db setup.

Revision ID: 2c2215d3e953
Revises:
Create Date: 2020-04-21 13:32:44.422928

"""
from alembic import op
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    String,
    Time,
    func,
)

# import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

import structlog
from sqlalchemy.sql.schema import ForeignKey

log = structlog.get_logger(__name__)

# revision identifiers, used by Alembic.
revision = "2c2215d3e953"
down_revision = None
branch_labels = None
depends_on = None

# create_type=False for ENUM: see
# https://bitbucket.org/zzzeek/alembic/issues/53/create-table-dont-create-enum

canadian_provinces = ENUM(
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
    name="canadian_province",
    create_type=False,
)

languages = ENUM("en", "fr", name="language", create_type=False,)

symptoms_severity = ENUM(
    "none", "moderate", "severe", name="symptoms_severity", create_type=False,
)


def upgrade():
    canadian_provinces.create(bind=op.get_bind(), checkfirst=True)
    languages.create(bind=op.get_bind(), checkfirst=True)
    symptoms_severity.create(bind=op.get_bind(), checkfirst=True)

    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    create_user_table()
    create_assesment_table()


def create_user_table():
    log.info("Creating user table.")

    op.create_table(
        "user",
        Column(
            "id",
            UUID(as_uuid=True),
            unique=True,
            server_default=func.uuid_generate_v4(),
        ),
        Column("first_name", String()),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("last_reminded_at", DateTime(timezone=True)),
        Column("reminder_time", Time(timezone=True), nullable=False),
        Column("preferred_language", languages, nullable=False),
        Column("resides_in", canadian_provinces, nullable=False),
        Column("date_of_birth", Date(), nullable=False),
        Column("has_preexisting_condition", Boolean(), nullable=False),
        Column("has_dialogue", Boolean()),
        Column("phone_number", String(), unique=True),
        Column(
            "is_phone_number_confirmed",
            Boolean(),
            nullable=False,
            server_default="false",
        ),
        Column("is_active", Boolean(), nullable=False, server_default="true"),
    )


def create_assesment_table():
    log.info("Creating assesment table.")

    op.create_table(
        "assesment",
        Column(
            "id",
            UUID(as_uuid=True),
            unique=True,
            server_default=func.uuid_generate_v4(),
        ),
        Column(
            "user_id",
            UUID(as_uuid=True),
            ForeignKey("user.id", onupdate="CASCADE", ondelete="SET NULL"),
            nullable=False,
        ),
        Column("completed_at", DateTime(timezone=True), nullable=False),
        Column("symptoms_severity", symptoms_severity),
        Column("has_fever", Boolean()),
        Column("has_cough", Boolean()),
        Column("has_difficulty_breathing", Boolean()),
        Column("feels_worse", Boolean()),
    )


def downgrade():
    op.drop_table("assesment")
    op.drop_table("user")

    symptoms_severity.drop(bind=op.get_bind())
    languages.drop(bind=op.get_bind())
    canadian_provinces.drop(bind=op.get_bind())
