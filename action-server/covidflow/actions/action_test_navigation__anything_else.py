from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import SELF_ASSESS_DONE_SLOT

from .lib.log_util import bind_logger


class ActionAskTestNavigationAnythingElse(Action):
    def name(self) -> Text:
        return "action_test_navigation__anything_else"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        if tracker.get_slot(SELF_ASSESS_DONE_SLOT) is True:
            dispatcher.utter_message(
                template="utter_test_navigation__anything_else_no_assessment"
            )
        else:
            dispatcher.utter_message(
                template="utter_test_navigation__anything_else_offer_assessment"
            )

        return []
