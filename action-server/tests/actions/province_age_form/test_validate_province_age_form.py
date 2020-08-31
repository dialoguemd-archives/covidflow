from covidflow.actions.province_age_form.validate_province_age_form import (
    FORM_NAME,
    ValidateProvinceAgeForm,
)
from covidflow.constants import AGE_OVER_65_SLOT, PROVINCE_SLOT
from tests.actions.validate_action_test_helper import ValidateActionTestCase


class ValidateProvinceAgeFormTest(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateProvinceAgeForm()
        self.form_name = FORM_NAME

    def test_valid_province_code(self):
        self.check_slot_value_accepted(PROVINCE_SLOT, "bc")

    def test_invalid_province_code(self):
        self.check_slot_value_rejected(PROVINCE_SLOT, "qg")

    def test_age_over_65_true(self):
        self.check_slot_value_accepted(AGE_OVER_65_SLOT, True)

    def test_age_over_65_false(self):
        self.check_slot_value_accepted(AGE_OVER_65_SLOT, False)
