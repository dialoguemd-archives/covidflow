import pytest

from covidflow.actions.self_isolation_form import FORM_NAME, ValidateSelfIsolationForm
from covidflow.constants import LIVES_ALONE_SLOT

from .validate_action_test_helper import ValidateActionTestCase


class ValidateSelfIsolationFormTest(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateSelfIsolationForm()
        self.form_name = FORM_NAME

    @pytest.mark.asyncio
    async def test_activation(self):
        await self.check_activation()

    @pytest.mark.asyncio
    async def test_lives_alone(self):
        templates = ["utter_lives_alone_true", "utter_self_isolation_final"]
        await self.check_slot_value_accepted(
            LIVES_ALONE_SLOT, True, templates=templates
        )

    @pytest.mark.asyncio
    async def test_does_not_live_alone(self):
        templates = [
            "utter_lives_alone_false_1",
            "utter_lives_alone_false_2",
            "utter_lives_alone_false_3",
            "utter_self_isolation_final",
        ]
        await self.check_slot_value_accepted(
            LIVES_ALONE_SLOT, False, templates=templates
        )
