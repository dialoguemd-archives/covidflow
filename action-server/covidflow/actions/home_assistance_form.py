from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .constants import HAS_ASSISTANCE_SLOT, PROVINCE_SLOT, PROVINCES_WITH_211

FORM_NAME = "home_assistance_form"


def _has_211(tracker: Tracker) -> bool:
    province = tracker.get_slot(PROVINCE_SLOT)
    return province in PROVINCES_WITH_211


class HomeAssistanceForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if _has_211(tracker):
            return [HAS_ASSISTANCE_SLOT]

        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            HAS_ASSISTANCE_SLOT: [
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

        if _has_211(tracker) and not tracker.get_slot(HAS_ASSISTANCE_SLOT):
            dispatcher.utter_message(template="utter_check_delivery_services")
            dispatcher.utter_message(template="utter_may_call_211")
            dispatcher.utter_message(template="utter_explain_211")
        else:
            dispatcher.utter_message(template="utter_remind_delivery_services")

        dispatcher.utter_message(template="utter_remind_pharmacist_services")

        return []
