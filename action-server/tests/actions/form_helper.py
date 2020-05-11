import asyncio
from typing import Dict, List
from unittest import TestCase

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

PHONE_TRY_COUNTER_SLOT = "daily_ci_enroll__phone_number_error_counter"
CODE_TRY_COUNTER_SLOT = "daily_ci_enroll__validation_code_error_counter"
WANTS_CANCEL_SLOT = "daily_ci_enroll__wants_cancel"
NO_CODE_SOLUTION_SLOT = "daily_ci_enroll__no_code_solution"

INITIAL_SLOT_VALUES = {
    PHONE_TRY_COUNTER_SLOT: 0,
    CODE_TRY_COUNTER_SLOT: 0,
    WANTS_CANCEL_SLOT: False,
    NO_CODE_SOLUTION_SLOT: "N/A",
}


class FormTestCase(TestCase):
    def setUp(self):
        self.dispatcher = CollectingDispatcher()
        self.form: FormAction = None

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
            {"name": self.form.name(), "validate": True, "rejected": False}
            if active_form
            else {},
            last_action,
        )

    def run_form(self, tracker: Tracker):
        loop = asyncio.get_event_loop()

        self.events = loop.run_until_complete(
            self.form.run(dispatcher=self.dispatcher, tracker=tracker, domain=None)
        )

        self.templates = [message["template"] for message in self.dispatcher.messages]

    def assert_events(self, expected_events: List[Dict]) -> None:
        self.assertEqual(self.events, expected_events)

    def assert_templates(self, expected_templates: List[str]) -> None:
        self.assertEqual(self.templates, expected_templates)
