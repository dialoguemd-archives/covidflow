import unittest
from typing import Dict

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.action_set_risk_level import ActionSetRiskLevel


def _create_tracker(slots: Dict = {}) -> Tracker:

    return Tracker("default", slots, {}, [], False, None, {}, "action_listen")


class ActionSetRiskLevelTest(unittest.TestCase):
    def test_action_name(self):

        assert ActionSetRiskLevel().name() == "action_set_risk_level"

    def test_no_symptoms_no_risk(self):
        tracker = _create_tracker()

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "common")
        ]

    def test_over_65(self):
        tracker = _create_tracker({"age_over_65": True})

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "elevated-medical-risk")
        ]

    def test_moderate_symptoms(self):
        tracker = _create_tracker({"symptoms": "moderate"})

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "elevated-medical-risk")
        ]

    def test_mild_symptoms(self):
        tracker = _create_tracker({"symptoms": "mild"})

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "common")
        ]

    def test_travel_risk(self):
        tracker = _create_tracker({"travel": True})

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "elevated-covid-risk")
        ]

    def test_contact_risk(self):
        tracker = _create_tracker({"contact": True})

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "elevated-covid-risk")
        ]

    def test_medical_and_covid_risk(self):
        tracker = _create_tracker({"age_over_65": True, "contact": True})

        assert ActionSetRiskLevel().run(CollectingDispatcher(), tracker, {}) == [
            SlotSet("risk_level", "elevated-medical-risk,elevated-covid-risk")
        ]
