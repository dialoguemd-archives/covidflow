from unittest import TestCase
from unittest.mock import Mock

from rasa_sdk import Tracker

from covidflow.actions.action_visit_package import (
    RISK_LEVEL_COVID,
    RISK_LEVEL_DEFAULT,
    RISK_LEVEL_MEDICAL,
    ActionVisitPackage,
)
from covidflow.constants import (
    ACTION_LISTEN_NAME,
    AGE_OVER_65_SLOT,
    CONTACT_SLOT,
    HAS_COUGH_SLOT,
    HAS_FEVER_SLOT,
    PROVINCE_SLOT,
    SYMPTOMS_SLOT,
    TRAVEL_SLOT,
    Symptoms,
)


def _create_tracker(slots={}) -> Tracker:
    return Tracker("default", {}, {}, [], False, None, {}, ACTION_LISTEN_NAME,)


class TestActionVisitPackage(TestCase):
    def assert_package_id(self, slots: dict, id: str) -> None:
        tracker = _create_tracker(slots)
        dispatcher_mock = Mock()
        ActionVisitPackage().run(dispatcher_mock, tracker, {})

        dispatcher_mock.utter_message.assert_called_once_with(
            template="utter_visit_package", id=id
        )

    def test_action_name(self):
        self.assertEqual(
            ActionVisitPackage().name(), "action_visit_package",
        )

        def test_risk_level_no_symptoms_no_risk(self):
            slots = {
                SYMPTOMS_SLOT: Symptoms.NONE,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
            }
            self.assert_package_id(slots, f"ca-qc,{RISK_LEVEL_DEFAULT}")

        def test_risk_level_over_65(self):

            slots = {
                SYMPTOMS_SLOT: Symptoms.NONE,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: True,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
            }

            self.assert_package_id(slots, f"ca-qc,{RISK_LEVEL_MEDICAL}"),

        def test_risk_level_moderate_symptoms(self):
            slots = {
                SYMPTOMS_SLOT: Symptoms.MODERATE,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
            }

            self.assert_package_id(slots, f"ca-qc,{RISK_LEVEL_MEDICAL}")

        def test_risk_level_mild_symptoms(self):
            slots = (
                {
                    SYMPTOMS_SLOT: Symptoms.MILD,
                    PROVINCE_SLOT: "qc",
                    AGE_OVER_65_SLOT: False,
                    HAS_FEVER_SLOT: False,
                    HAS_COUGH_SLOT: True,
                },
            )

            self.assert_package_id(slots, f"ca-qc,{RISK_LEVEL_DEFAULT}"),

        def test_risk_level_travel_risk(self):
            slots = {
                SYMPTOMS_SLOT: Symptoms.NONE,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                TRAVEL_SLOT: True,
            }

            self.assert_package_id(slots, f"ca-qc,{RISK_LEVEL_COVID}")

        def test_risk_level_contact_risk(self):
            slots = {
                SYMPTOMS_SLOT: Symptoms.NONE,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                CONTACT_SLOT: True,
            }

            self.assert_package_id(slots, f"ca-qc,{RISK_LEVEL_COVID}")

        def test_risk_level_medical_and_covid_risk(self):
            slots = {
                SYMPTOMS_SLOT: Symptoms.NONE,
                PROVINCE_SLOT: "qc",
                AGE_OVER_65_SLOT: True,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
                TRAVEL_SLOT: True,
            }

            self.assert_package_id(
                slots, f"ca-qc,{RISK_LEVEL_MEDICAL},{RISK_LEVEL_COVID}"
            )

        def test_no_province(self):
            slots = {
                SYMPTOMS_SLOT: Symptoms.NONE,
                AGE_OVER_65_SLOT: False,
                HAS_FEVER_SLOT: False,
                HAS_COUGH_SLOT: False,
            }

            self.assert_package_id(slots, f"{RISK_LEVEL_DEFAULT}")
