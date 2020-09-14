from rasa_sdk.events import ActionExecuted, ActionReverted, FollowupAction, UserUttered

from covidflow.actions.action_check_task_allowed import ActionCheckTaskAllowed
from covidflow.actions.action_default_fallback import (
    ACTION_NAME as FALLBACK_ACTION_NAME,
)
from covidflow.constants import ACTION_LISTEN_NAME

from .action_test_helper import ActionTestCase

ACTION = "utter_ask_assess_after_error"
ALLOWED_INTENT = "get_assessment"
FORBIDDEN_INTENT = "ask_question"

LATEST_EVENTS = [ActionExecuted(ACTION), ActionExecuted(ACTION_LISTEN_NAME)]


class ActionCheckTaskAllowedTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionCheckTaskAllowed()

    def test_task_allowed(self):
        tracker = self.create_tracker(
            intent=ALLOWED_INTENT,
            events=LATEST_EVENTS
            + [UserUttered(text="text", parse_data={"intent": ALLOWED_INTENT})],
        )

        self.run_action(tracker)

        self.assert_events([])

        self.assert_templates([])

    def test_task_not_allowed(self):
        tracker = self.create_tracker(
            intent=FORBIDDEN_INTENT,
            events=LATEST_EVENTS
            + [UserUttered(text="text", parse_data={"intent": FORBIDDEN_INTENT})],
        )

        self.run_action(tracker)

        self.assert_events([ActionReverted(), FollowupAction(FALLBACK_ACTION_NAME)])

        self.assert_templates([])

    def test_action_not_in_list(self):
        tracker = self.create_tracker(
            intent=FORBIDDEN_INTENT,
            events=[
                ActionExecuted("action_another"),
                ActionExecuted(ACTION_LISTEN_NAME),
                UserUttered(text="text", parse_data={"intent": FORBIDDEN_INTENT}),
            ],
        )

        self.run_action(tracker)

        self.assert_events([ActionReverted(), FollowupAction(FALLBACK_ACTION_NAME)])

        self.assert_templates([])
