from rasa_sdk.events import SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.home_assistance_form import FORM_NAME, ValidateHomeAssistanceForm
from covidflow.constants import (
    HAS_ASSISTANCE_SLOT,
    PROVINCE_SLOT,
    SKIP_SLOT_PLACEHOLDER,
)

from .validate_action_test_helper import ValidateActionTestCase


class ValidateHomeAssistanceFormTest(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateHomeAssistanceForm()
        self.form_name = FORM_NAME

    def test_activate_has_211(self):
        slots = {PROVINCE_SLOT: "sk"}
        self.check_activation(previous_slots=slots)

    def test_activate_does_not_have_211(self):
        slots = {PROVINCE_SLOT: "nl"}
        events = [
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(HAS_ASSISTANCE_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]
        templates = [
            "utter_home_assistance_offer_211_false",
            "utter_home_assistance_final",
        ]
        self.check_activation(events=events, previous_slots=slots, templates=templates)

    def test_has_assistance(self):
        templates = [
            "utter_home_assistance_offer_211_false",
            "utter_home_assistance_final",
        ]
        self.check_slot_value_accepted(HAS_ASSISTANCE_SLOT, True, templates=templates)

    def test_does_not_have_assistance_qc(self):
        slots = {PROVINCE_SLOT: "qc"}
        templates = [
            "utter_home_assistance_offer_211_true_1",
            "utter_home_assistance_offer_211_true_2_qc",
            "utter_home_assistance_offer_211_true_3",
            "utter_home_assistance_final",
        ]
        self.check_slot_value_accepted(
            HAS_ASSISTANCE_SLOT, False, templates=templates, previous_slots=slots
        )

    def test_does_not_have_assistance_other(self):
        slots = {PROVINCE_SLOT: "sk"}
        templates = [
            "utter_home_assistance_offer_211_true_1",
            "utter_home_assistance_offer_211_true_2_other",
            "utter_home_assistance_offer_211_true_3",
            "utter_home_assistance_final",
        ]
        self.check_slot_value_accepted(
            HAS_ASSISTANCE_SLOT, False, templates=templates, previous_slots=slots
        )
