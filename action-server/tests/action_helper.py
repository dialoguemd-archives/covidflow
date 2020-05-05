from typing import Dict, List
from unittest import TestCase

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

PHONE_TRY_COUNTER_SLOT = "daily_ci_enroll__phone_number_error_counter"
CODE_TRY_COUNTER_SLOT = "daily_ci_enroll__validation_code_error_counter"
WANTS_CANCEL_SLOT = "daily_ci_enroll__wants_cancel"

INITIAL_SLOT_VALUES = {
    PHONE_TRY_COUNTER_SLOT: 0,
    CODE_TRY_COUNTER_SLOT: 0,
    WANTS_CANCEL_SLOT: False,
}


class ActionTestCase(TestCase):
    def setUp(self):
        self.dispatcher = CollectingDispatcher()
        self.action: Action = None

    def create_tracker(
        self,
        sender_id: str = "default",
        slots: dict = None,
        events: List[Dict] = None,
        paused: bool = False,
        followup_action: str = None,
        intent: str = None,
        entities: list = None,
        text: str = None,
        active_form: bool = True,
        last_action: str = "action_listen",
    ) -> Tracker:
        all_slots = {}
        all_slots.update(INITIAL_SLOT_VALUES)
        all_slots.update(slots or {})
        return Tracker(
            sender_id,
            all_slots,
            {
                "intent": {"name": intent or "none"},
                "entities": entities or [],
                "text": text or "",
            },
            events or [],
            paused,
            followup_action,
            {},
            last_action,
        )

    def run_action(self, tracker: Tracker):
        self.events = self.action.run(
            dispatcher=self.dispatcher, tracker=tracker, domain=None
        )

        self.templates = [message["template"] for message in self.dispatcher.messages]

    def assert_events(self, expected_events: List[Dict]) -> None:
        self.assertEqual(self.events, expected_events)

    def assert_templates(self, expected_templates: List[str]) -> None:
        self.assertEqual(self.templates, expected_templates)
