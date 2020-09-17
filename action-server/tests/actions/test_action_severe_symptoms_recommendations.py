import pytest
from rasa_sdk.events import ConversationPaused

from covidflow.actions.action_severe_symptoms_recommendations import (
    ActionSevereSymptomsRecommendations,
)
from covidflow.constants import END_CONVERSATION_MESSAGE

from .action_test_helper import ActionTestCase


class ActionSevereSymptomsRecommendationsTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionSevereSymptomsRecommendations()

    @pytest.mark.asyncio
    async def test_recommendations(self):
        tracker = self.create_tracker()

        await self.run_action(tracker)

        self.assert_events([ConversationPaused()])

        self.assert_templates(
            [
                "utter_severe_symptoms_recommendations_1",
                "utter_severe_symptoms_recommendations_2",
                "utter_severe_symptoms_recommendations_3",
                "utter_severe_symptoms_recommendations_4",
                None,
            ]
        )

        self.assert_json_messages([{}, {}, {}, {}, END_CONVERSATION_MESSAGE])
