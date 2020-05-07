from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.action_daily_ci_recommendations import (
    ACTION_NAME as RECOMMENDATIONS_ACTION_NAME,
)
from actions.form_helper import request_next_slot
from actions.lib.persistence import cancel_reminder

FORM_NAME = "daily_ci_keep_or_cancel_form"

AGE_OVER_65_SLOT = "age_over_65"
CANCEL_CI_SLOT = "cancel_ci"
FEEL_WORSE_SLOT = "feel_worse"
PRECONDITIONS_SLOT = "preconditions"
SYMPTOMS_SLOT = "symptoms"


class DailyCiKeepOrCancelForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    ## override to play initial message
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if (
            tracker.active_form.get("name") != FORM_NAME
            and tracker.get_slot(SYMPTOMS_SLOT) == "none"
        ):
            dispatcher.utter_message(
                template="utter_daily_ci__keep_or_cancel__no_symptoms_recommendation"
            )

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return [] if _mandatory_ci(tracker) else [CANCEL_CI_SLOT]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            CANCEL_CI_SLOT: [
                self.from_intent(intent="cancel", value=True),
                self.from_intent(intent="continue", value=False),
            ],
        }

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        return request_next_slot(
            self, dispatcher, tracker, domain, self._utter_ask_slot_template
        )

    def _utter_ask_slot_template(self, slot: str, tracker: Tracker) -> Optional[str]:
        if slot == CANCEL_CI_SLOT:
            if tracker.get_slot(SYMPTOMS_SLOT) == "none":
                return f"utter_ask_daily_ci__keep_or_cancel__{slot}_no_symptoms"
            else:
                return f"utter_ask_daily_ci__keep_or_cancel__{slot}_symptoms"

        return None

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        # Mandatory check-in
        if _mandatory_ci(tracker):
            dispatcher.utter_message(
                template="utter_daily_ci__keep_or_cancel__feel_worse_keep_ci"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__keep_or_cancel__feel_worse_recommendation"
            )
            return [FollowupAction(RECOMMENDATIONS_ACTION_NAME)]

        # Optional check-in cancel
        elif tracker.get_slot(CANCEL_CI_SLOT) is True:
            dispatcher.utter_message(
                template="utter_daily_ci__keep_or_cancel__acknowledge_cancel_ci"
            )
            dispatcher.utter_message(
                template="utter_daily_ci__keep_or_cancel__cancel_ci_recommendation"
            )
            cancel_reminder(tracker.current_slot_values())
            return []

        # Optional check-in continue
        dispatcher.utter_message(
            template="utter_daily_ci__keep_or_cancel__acknowledge_continue_ci"
        )

        if tracker.get_slot(SYMPTOMS_SLOT) == "none":
            return []

        return [FollowupAction(RECOMMENDATIONS_ACTION_NAME)]


def _mandatory_ci(tracker: Tracker) -> bool:
    if tracker.get_slot(SYMPTOMS_SLOT) == "none":
        return False

    if tracker.get_slot(FEEL_WORSE_SLOT) is True:
        return (
            tracker.get_slot(SYMPTOMS_SLOT) == "moderate"
            or tracker.get_slot(PRECONDITIONS_SLOT) is True
            or tracker.get_slot(AGE_OVER_65_SLOT) is True
        )

    return False
