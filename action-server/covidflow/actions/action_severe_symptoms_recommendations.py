from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ConversationPaused
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import END_CONVERSATION_MESSAGE

from .lib.log_util import bind_logger


class ActionSevereSymptomsRecommendations(Action):
    def name(self) -> Text:
        return "action_severe_symptoms_recommendations"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        dispatcher.utter_message(template="utter_severe_symptoms_recommendations_1")
        dispatcher.utter_message(template="utter_severe_symptoms_recommendations_2")
        dispatcher.utter_message(template="utter_severe_symptoms_recommendations_3")
        dispatcher.utter_message(template="utter_severe_symptoms_recommendations_4")

        dispatcher.utter_message(json_message=END_CONVERSATION_MESSAGE)

        return [ConversationPaused()]
