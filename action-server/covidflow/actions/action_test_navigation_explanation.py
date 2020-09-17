from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import PROVINCIAL_811_SLOT

from .lib.log_util import bind_logger
from .lib.provincial_811 import get_provincial_811


class ActionTestNavigationExplanations(Action):
    def name(self) -> Text:
        return "action_test_navigation_explanations"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)

        variables = {}
        if tracker.get_slot(PROVINCIAL_811_SLOT) is None:
            variables[PROVINCIAL_811_SLOT] = get_provincial_811(None, domain)
        dispatcher.utter_message(
            template="utter_test_navigation__explanations_1", **variables
        )
        dispatcher.utter_message(
            template="utter_test_navigation__explanations_2", **variables
        )
        dispatcher.utter_message(
            template="utter_test_navigation__explanations_3", **variables
        )
        dispatcher.utter_message(
            template="utter_test_navigation__explanations_4", **variables
        )

        return []
