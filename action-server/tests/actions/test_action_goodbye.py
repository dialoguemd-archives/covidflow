import pytest
from rasa_sdk.events import ConversationPaused

from covidflow.actions.action_goodbye import ActionGoodbye

from .action_test_helper import ActionTestCase


class ActionGoodbyeTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionGoodbye()

    @pytest.mark.asyncio
    async def test_goodbye(self):
        tracker = self.create_tracker()

        await self.run_action(tracker)

        self.assert_events([ConversationPaused()])

        self.assert_templates(["utter_goodbye"])
