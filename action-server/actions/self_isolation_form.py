from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

LIVES_ALONE_SLOT = "lives_alone"


class SelfIsolationForm(FormAction):
    def name(self) -> Text:

        return "self_isolation_form"

    ## override to play initial message
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_form.get("name") != "self_isolation_form":
            dispatcher.utter_message(template="utter_symptoms_self_isolate")

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return [LIVES_ALONE_SLOT]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            LIVES_ALONE_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if tracker.get_slot(LIVES_ALONE_SLOT):
            dispatcher.utter_message(
                template="utter_dont_leave_home_unless_appointment"
            )
        else:
            dispatcher.utter_message(template="utter_stay_separate_room")
            dispatcher.utter_message(template="utter_distance_clean_surfaces")
            dispatcher.utter_message(template="utter_wear_mask_same_room")

        dispatcher.utter_message(template="utter_self_isolation_link")

        return []
