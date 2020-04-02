from unittest import TestCase

from actions.action_cheer_up import ActionCheerUp


class TestActionCheerUp(TestCase):
    def test_name(self):
        self.assertEqual(ActionCheerUp().name(), "action_cheer_up")
