import unittest

from actions.lib.phone_number_validation import generate_validation_code


class PhoneNumberValidationTest(unittest.TestCase):
    def test_generate_validation_code(self):
        validation_code = generate_validation_code()
        self.assertEqual(len(validation_code), 4)
        self.assertTrue(validation_code.isnumeric())
