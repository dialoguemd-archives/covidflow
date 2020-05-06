from rasa_sdk.events import SlotSet

from actions.action_daily_ci_early_opt_out import (
    CANCEL_CI_SLOT,
    ActionDailyCiEarlyOptOut,
)
from tests.action_helper import ActionTestCase


class ActionDailyCiEarlyOptOutTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionDailyCiEarlyOptOut()

    def test_early_opt_out(self):
        tracker = self.create_tracker()

        self.run_action(tracker)

        self.assert_events([SlotSet(CANCEL_CI_SLOT, True)])

        self.assert_templates(
            [
                "utter_daily_ci__early_opt_out__acknowledge_cancel_ci",
                "utter_daily_ci__early_opt_out__cancel_ci_recommendation",
            ]
        )
