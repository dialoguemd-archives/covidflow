from rasa_sdk.events import ConversationPaused

from covidflow.actions.action_severe_symptoms_recommendations import (
    ActionSevereSymptomsRecommendations,
)
from covidflow.actions.constants import END_CONVERSATION_MESSAGE

from .action_helper import ActionTestCase


class ActionSevereSymptomsRecommendationsTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionSevereSymptomsRecommendations()

    def test_recommendations(self):
        tracker = self.create_tracker()

        self.run_action(tracker)

        self.assert_events([ConversationPaused()])

        self.assert_templates(["utter_call_911", None])

        self.assert_json_messages([{}, END_CONVERSATION_MESSAGE])
