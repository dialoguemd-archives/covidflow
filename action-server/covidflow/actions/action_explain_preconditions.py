from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher


class ActionExplainPreconditions(Action):
    def name(self) -> Text:
        return "action_explain_preconditions"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_template("utter_explain_preconditions", tracker)
        dispatcher.utter_template("utter_ask_preconditions_again", tracker)

        return [UserUtteranceReverted()]
