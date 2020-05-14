"""Fix test profiles.

Revision ID: 00003
Revises:
Create Date: 2020-05-14

"""

import structlog

from alembic import op

log = structlog.get_logger()

revision = "00003"
down_revision = "00002"
branch_labels = None
depends_on = None

REMINDER_TABLE = "reminder"
ASSESSMENT_TABLE = "assessment"

OLD_TEST_PROFILE_REVISION = "rev_00002"
NEW_TEST_PROFILE_REVISION = "rev_00003"


def upgrade():
    op.execute(
        (
            f"update reminder set attributes = attributes"
            f"   || jsonb_build_object('province', substring(attributes->>'province' from 4))"
            f"   || jsonb_build_object('test_profile', '{NEW_TEST_PROFILE_REVISION}')"
            f" where attributes->>'test_profile' = '{OLD_TEST_PROFILE_REVISION}'"
        )
    )

    op.execute(
        (
            f"update assessment set attributes = attributes"
            f"   || jsonb_build_object('test_profile', '{NEW_TEST_PROFILE_REVISION}')"
            f" where attributes->>'test_profile' = '{OLD_TEST_PROFILE_REVISION}'"
        )
    )


def downgrade():
    log.info("Removing test profiles from reminder table.")

    op.execute(
        (
            f"update reminder set attributes = attributes"
            f"   || jsonb_build_object('province', concat('ca-', attributes->>'province'))"
            f"   || jsonb_build_object('test_profile', '{OLD_TEST_PROFILE_REVISION}')"
            f" where attributes->>'test_profile' = '{NEW_TEST_PROFILE_REVISION}'"
        )
    )

    op.execute(
        (
            f"update assessment set attributes = attributes"
            f"   || jsonb_build_object('test_profile', '{OLD_TEST_PROFILE_REVISION}')"
            f" where attributes->>'test_profile' = '{NEW_TEST_PROFILE_REVISION}'"
        )
    )
