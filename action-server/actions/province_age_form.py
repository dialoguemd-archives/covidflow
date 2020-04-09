from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction


class ProvinceAgeForm(FormAction):
    def name(self) -> Text:

        return "province_age_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["province", "age_over_65"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "age_over_65": [
                    self.from_intent(intent="affirm", value=True),
                    self.from_intent(intent="deny", value=False),
            ]
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:

        return []
