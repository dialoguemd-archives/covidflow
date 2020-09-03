from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.home_assistance_form import FORM_NAME, HomeAssistanceForm
from covidflow.constants import HAS_ASSISTANCE_SLOT, PROVINCE_SLOT

from .form_test_helper import FormTestCase

DOMAIN = {"responses": {"utter_ask_has_assistance_error": [{"text": ""}],}}


class TestHomeAssistanceForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = HomeAssistanceForm()

    def test_not_has_211(self):
        tracker = self.create_tracker(active_loop=False, slots={PROVINCE_SLOT: "nu"})

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), ActiveLoop(None), SlotSet(REQUESTED_SLOT, None)]
        )

        self.assert_templates(
            ["utter_remind_delivery_services", "utter_remind_pharmacist_services"]
        )

    def test_has_211(self):
        tracker = self.create_tracker(active_loop=False, slots={PROVINCE_SLOT: "qc"})

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, HAS_ASSISTANCE_SLOT)]
        )

        self.assert_templates(["utter_ask_has_assistance"])

    def test_has_211_has_assistance(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_ASSISTANCE_SLOT, PROVINCE_SLOT: "qc"},
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_ASSISTANCE_SLOT, True),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            ["utter_remind_delivery_services", "utter_remind_pharmacist_services"]
        )

    def test_has_211_not_has_assistance_qc(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_ASSISTANCE_SLOT, PROVINCE_SLOT: "qc"},
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_ASSISTANCE_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_check_delivery_services",
                "utter_may_call_211_qc",
                "utter_explain_211",
                "utter_remind_pharmacist_services",
            ]
        )

    def test_has_211_not_has_assistance_other_province(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_ASSISTANCE_SLOT, PROVINCE_SLOT: "bc"},
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_ASSISTANCE_SLOT, False),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(
            [
                "utter_check_delivery_services",
                "utter_may_call_211_other_provinces",
                "utter_explain_211",
                "utter_remind_pharmacist_services",
            ]
        )

    def test_has_211_has_assistance_error(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: HAS_ASSISTANCE_SLOT, PROVINCE_SLOT: "bc"},
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(HAS_ASSISTANCE_SLOT, None),
                SlotSet(REQUESTED_SLOT, HAS_ASSISTANCE_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_has_assistance_error"])
