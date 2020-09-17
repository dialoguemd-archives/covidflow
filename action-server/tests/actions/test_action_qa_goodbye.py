import pytest
from rasa_sdk.events import ConversationPaused

from covidflow.actions.action_qa_goodbye import ActionQaGoodbye
from covidflow.constants import CONTINUE_CI_SLOT

from .action_test_helper import ActionTestCase


class ActionQAGoodbyeTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionQaGoodbye()

    @pytest.mark.asyncio
    async def test_continue_ci_true(self):
        tracker = self.create_tracker(slots={CONTINUE_CI_SLOT: True})

        await self.run_action(tracker)

        self.assert_events([ConversationPaused()])

        self.assert_templates(
            ["utter_daily_ci__qa__will_contact_tomorrow", "utter_goodbye"]
        )

    @pytest.mark.asyncio
    async def test_continue_ci_false(self):
        tracker = self.create_tracker(slots={CONTINUE_CI_SLOT: False})

        await self.run_action(tracker)

        self.assert_events([ConversationPaused()])

        self.assert_templates(["utter_goodbye"])
