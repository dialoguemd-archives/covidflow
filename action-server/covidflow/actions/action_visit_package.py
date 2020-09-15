from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import (
    AGE_OVER_65_SLOT,
    HAS_CONTACT_RISK_SLOT,
    PROVINCE_SLOT,
    SYMPTOMS_SLOT,
    Symptoms,
)

from .lib.log_util import bind_logger

RISK_LEVEL_MEDICAL = "elevated-medical-risk"
RISK_LEVEL_COVID = "elevated-covid-risk"
RISK_LEVEL_DEFAULT = "common"


class ActionVisitPackage(Action):
    def name(self) -> Text:
        return "action_visit_package"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        bind_logger(tracker)
        province = tracker.get_slot(PROVINCE_SLOT)
        risk_level = _get_risk_level_value(tracker)

        id = f"{province},{risk_level}" if province is not None else risk_level

        dispatcher.utter_message(template="utter_visit_package", id=id)

        return []


def _get_risk_level_value(tracker: Tracker) -> str:
    risk_level_value = []
    if (
        tracker.get_slot(AGE_OVER_65_SLOT) is True
        or tracker.get_slot(SYMPTOMS_SLOT) == Symptoms.MODERATE
    ):
        risk_level_value.append(RISK_LEVEL_MEDICAL)
    if tracker.get_slot(HAS_CONTACT_RISK_SLOT) is True:
        risk_level_value.append(RISK_LEVEL_COVID)

    return RISK_LEVEL_DEFAULT if risk_level_value == [] else ",".join(risk_level_value)
