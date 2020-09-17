import pytest
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.contact_risk_form import FORM_NAME, ValidateContactRiskForm
from covidflow.constants import (
    CONTACT_SLOT,
    HAS_CONTACT_RISK_SLOT,
    SKIP_SLOT_PLACEHOLDER,
    TRAVEL_SLOT,
)

from .validate_action_test_helper import ValidateActionTestCase


class ValidateContactRiskFormTest(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateContactRiskForm()
        self.form_name = FORM_NAME

    @pytest.mark.asyncio
    async def test_activation(self):
        await self.check_activation()

    @pytest.mark.asyncio
    async def test_contact(self):
        extra_events = [
            SlotSet(HAS_CONTACT_RISK_SLOT, True),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(TRAVEL_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]
        await self.check_slot_value_accepted(
            CONTACT_SLOT, True, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_no_contact(self):
        await self.check_slot_value_accepted(CONTACT_SLOT, False)

    @pytest.mark.asyncio
    async def test_travel(self):
        extra_events = [SlotSet(HAS_CONTACT_RISK_SLOT, True)]
        await self.check_slot_value_accepted(
            TRAVEL_SLOT, True, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_no_travel(self):
        extra_events = [SlotSet(HAS_CONTACT_RISK_SLOT, False)]
        await self.check_slot_value_accepted(
            TRAVEL_SLOT, False, extra_events=extra_events
        )
