from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from ..lib.persistence import cancel_reminder

ACTION_NAME = "action_daily_ci_early_opt_out"

CANCEL_CI_SLOT = "cancel_ci"


class ActionDailyCiEarlyOptOut(Action):
    def name(self) -> Text:
        return ACTION_NAME

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            template="utter_daily_ci__early_opt_out__acknowledge_cancel_ci"
        )

        dispatcher.utter_message(
            template="utter_daily_ci__early_opt_out__cancel_ci_recommendation"
        )

        cancel_reminder(tracker.current_slot_values())

        return [SlotSet(CANCEL_CI_SLOT, True)]
