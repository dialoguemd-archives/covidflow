from rasa_sdk.events import ConversationPaused

from actions.action_goodbye import ActionGoodbye
from tests.action_helper import ActionTestCase


class ActionGoodbyeTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionGoodbye()

    def test_goodbye(self):
        tracker = self.create_tracker()

        self.run_action(tracker)

        self.assert_events([ConversationPaused()])

        self.assert_templates(["utter_goodbye"])
