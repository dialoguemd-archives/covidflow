"""Add test profiles to db.

Revision ID: 00002
Revises:
Create Date: 2020-05-13

"""
import os
from copy import deepcopy

import structlog
from hashids import Hashids
from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import table
from sqlalchemy.sql.schema import CheckConstraint, ForeignKey
from sqlalchemy.types import Integer, String

from alembic import op

log = structlog.get_logger()

revision = "00002"
down_revision = "00001"
branch_labels = None
depends_on = None

REMINDER_TABLE = "reminder"
ASSESSMENT_TABLE = "assessment"

TEST_PROFILE_REVISION = "rev_00002"


HASHIDS_SALT_ENV_KEY = "REMINDER_ID_HASHIDS_SALT"
HASHIDS_MIN_LENGTH_ENV_KEY = "REMINDER_ID_HASHIDS_MIN_LENGTH"


def create_hashids():
    salt = os.environ[HASHIDS_SALT_ENV_KEY]
    min_length = os.environ[HASHIDS_MIN_LENGTH_ENV_KEY]
    return Hashids(salt, min_length=min_length)


def encode_reminder_id(reminder_id: int) -> str:
    return create_hashids().encode(reminder_id)


class TestProfile:
    def __init__(self):
        self.reminder_attributes: dict = {}
        self.assessment_attributes: dict = {}

    def set_reminder_attributes(
        self,
        first_name: str,
        phone_number: str,
        language: str,
        province: str,
        age_over_65: bool,
        preconditions: bool,
        has_dialogue: bool,
    ):
        self.reminder_attributes = {
            "test_profile": TEST_PROFILE_REVISION,
            "first_name": first_name,
            "phone_number": phone_number,
            "language": language,
            "province": province,
            "age_over_65": age_over_65,
            "preconditions": preconditions,
            "has_dialogue": has_dialogue,
        }

        return self

    def set_assessment_attributes(
        self, symptoms: str, has_fever: bool, has_cough: bool, has_diff_breathing: bool,
    ):
        self.assessment_attributes = {
            "test_profile": TEST_PROFILE_REVISION,
            "symptoms": symptoms,
            "has_fever": has_fever,
            "has_cough": has_cough,
            "has_diff_breathing": has_diff_breathing,
            "feel_worse": False,
        }

        return self

    def create_reminder(self, timezone: str = "America/Toronto") -> dict:
        return {
            "timezone": timezone,
            "attributes": deepcopy(self.reminder_attributes),
        }

    def create_assessment(self, reminder_id: int) -> dict:
        return {
            "reminder_id": reminder_id,
            "attributes": deepcopy(self.assessment_attributes),
        }


TEST_PROFILE_1 = (
    TestProfile()
    .set_reminder_attributes(
        first_name="Mike",
        phone_number="15145551234",
        language="en",
        province="ca-on",
        age_over_65=False,
        preconditions=False,
        has_dialogue=False,
    )
    .set_assessment_attributes(
        symptoms="mild", has_fever=False, has_cough=False, has_diff_breathing=False
    )
)

TEST_PROFILE_2 = (
    TestProfile()
    .set_reminder_attributes(
        first_name="Kim",
        phone_number="15145552345",
        language="en",
        province="ca-ab",
        age_over_65=False,
        preconditions=True,
        has_dialogue=True,
    )
    .set_assessment_attributes(
        symptoms="moderate", has_fever=True, has_cough=True, has_diff_breathing=False
    )
)

TEST_PROFILE_3 = (
    TestProfile()
    .set_reminder_attributes(
        first_name="Maurice",
        phone_number="15145553456",
        language="fr",
        province="ca-nt",
        age_over_65=True,
        preconditions=False,
        has_dialogue=False,
    )
    .set_assessment_attributes(
        symptoms="mild", has_fever=False, has_cough=False, has_diff_breathing=True
    )
)

TEST_PROFILE_4 = (
    TestProfile()
    .set_reminder_attributes(
        first_name="Jane",
        phone_number="15145554567",
        language="fr",
        province="ca-qc",
        age_over_65=True,
        preconditions=True,
        has_dialogue=True,
    )
    .set_assessment_attributes(
        symptoms="moderate", has_fever=True, has_cough=True, has_diff_breathing=True
    )
)

TEST_PROFILES = [TEST_PROFILE_1, TEST_PROFILE_2, TEST_PROFILE_3, TEST_PROFILE_4]


def upgrade():
    reminder_table = _create_reminder_table_construct()
    assessment_table = _create_assessment_table_construct()

    _create_test_profiles(reminder_table, assessment_table, TEST_PROFILES)


def downgrade():
    _delete_test_profiles()


def _create_reminder_table_construct():
    log.info("Creating reminder table construct.")

    return table(
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


def _create_assessment_table_construct():
    log.info("Creating assessment table construct.")

    return table(
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


def _create_test_profiles(reminder_table, assessment_table, profiles):
    log.info("Adding test profiles to reminder table.")

    reminders = [test_profile.create_reminder() for test_profile in profiles]

    op.bulk_insert(reminder_table, reminders)

    log.info("Fetching test profiles reminder ids.")

    connection = op.get_bind()
    reminders = connection.execute(
        f"select id, attributes->>'phone_number' from {REMINDER_TABLE} where attributes->>'test_profile' = '{TEST_PROFILE_REVISION}';"
    )

    log.info("Adding test profiles to assessment table.")

    assessments = []

    for reminder in reminders:
        reminder_id = reminder[0]
        phone_number = reminder[1]

        hashed_reminder_id = encode_reminder_id(reminder.id)

        log.info(
            f"reminder_id={reminder_id}, hashed reminder_id={hashed_reminder_id}, phone_number={phone_number}"
        )

        profile = next(
            (
                profile
                for profile in profiles
                if profile.reminder_attributes["phone_number"] == phone_number
            ),
            None,
        )

        if profile is None:
            raise Exception(f"Could not find profile for phone number {phone_number}.")

        assessment = profile.create_assessment(reminder_id)
        assessments.append(assessment)

    op.bulk_insert(assessment_table, assessments)


def _delete_test_profiles():
    log.info("Removing test profiles from reminder table.")

    op.execute(
        f"DELETE FROM {REMINDER_TABLE} WHERE attributes->>'test_profile' = '{TEST_PROFILE_REVISION}'"
    )

    log.info("Removing test profiles from assessment table.")

    op.execute(
        f"DELETE FROM {ASSESSMENT_TABLE} WHERE attributes->>'test_profile' = '{TEST_PROFILE_REVISION}'"
    )
