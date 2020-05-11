from unittest.mock import patch

from rasa_sdk.events import SlotSet

from covidflow.actions.action_daily_ci_early_opt_out import (
    CANCEL_CI_SLOT,
    ActionDailyCiEarlyOptOut,
)
from tests.action_helper import ActionTestCase


class ActionDailyCiEarlyOptOutTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionDailyCiEarlyOptOut()

    @patch("covidflow.actions.action_daily_ci_early_opt_out.cancel_reminder")
    def test_early_opt_out(self, mock_cancel_reminder):
        tracker = self.create_tracker()

        self.run_action(tracker)

        self.assert_events([SlotSet(CANCEL_CI_SLOT, True)])

        self.assert_templates(
            [
                "utter_daily_ci__early_opt_out__acknowledge_cancel_ci",
                "utter_daily_ci__early_opt_out__cancel_ci_recommendation",
            ]
        )

        mock_cancel_reminder.assert_called()
