from unittest import TestCase

from actions.action import action


class TestActionGreet(TestCase):
    def test_action(self):
        self.assertEqual(action(), "done")
