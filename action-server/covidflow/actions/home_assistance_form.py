from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from covidflow.constants import HAS_ASSISTANCE_SLOT, PROVINCE_SLOT, PROVINCES_WITH_211

from .lib.form_helper import (
    request_next_slot,
    validate_boolean_slot,
    yes_no_nlu_mapping,
)
from .lib.log_util import bind_logger

FORM_NAME = "home_assistance_form"


def _has_211(tracker: Tracker) -> bool:
    province = tracker.get_slot(PROVINCE_SLOT)
    return province in PROVINCES_WITH_211


class HomeAssistanceForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if _has_211(tracker):
            return [HAS_ASSISTANCE_SLOT]

        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            HAS_ASSISTANCE_SLOT: yes_no_nlu_mapping(self),
        }

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        return request_next_slot(self, dispatcher, tracker, domain, None)

    @validate_boolean_slot
    def validate_has_assistance(
        self,
        value: Union[bool, Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        return {}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        if _has_211(tracker) and not tracker.get_slot(HAS_ASSISTANCE_SLOT):
            dispatcher.utter_message(template="utter_check_delivery_services")
            if tracker.get_slot(PROVINCE_SLOT) == "qc":
                dispatcher.utter_message(template="utter_may_call_211_qc")
            else:
                dispatcher.utter_message(template="utter_may_call_211_other_provinces")
            dispatcher.utter_message(template="utter_explain_211")
        else:
            dispatcher.utter_message(template="utter_remind_delivery_services")

        dispatcher.utter_message(template="utter_remind_pharmacist_services")

        return []
