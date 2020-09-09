from covidflow.actions.new_assessment_form.action_ask_province_code import (
    ActionAskProvinceCode,
)
from tests.actions.action_test_helper import ActionTestCase


class ActionAskProvinceCodeTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskProvinceCode()

    def test_ask_province_code(self):
        tracker = self.create_tracker()

        self.run_action(tracker)

        self.assert_templates(
            ["utter_pre_ask_province_code", "utter_ask_province_code"]
        )
