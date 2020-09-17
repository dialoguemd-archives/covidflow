from typing import Any, Dict, List, Optional, Text
from unittest import TestCase

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from covidflow.constants import ACTION_LISTEN_NAME

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
        active_loop: bool = False,
        last_action: str = ACTION_LISTEN_NAME,
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
            {"name": "some_form", "validate": True, "rejected": False}
            if active_loop
            else {},
            last_action,
        )

    async def run_action(
        self, tracker: Tracker, domain: Optional[Dict[Text, Any]] = None
    ):
        domain = domain or {}
        self.events = await self.action.run(
            dispatcher=self.dispatcher, tracker=tracker, domain=domain
        )

        self.templates = [message["template"] for message in self.dispatcher.messages]
        self.json_messages = [message["custom"] for message in self.dispatcher.messages]
        self.texts = [message["text"] for message in self.dispatcher.messages]
        self.attachments = [
            message["attachment"] for message in self.dispatcher.messages
        ]

    def assert_events(self, expected_events: List[Dict]) -> None:
        self.assertEqual(self.events, expected_events)

    # If a message does not contain templates, it appears as None in the list
    def assert_templates(self, expected_templates: List[str]) -> None:
        self.assertEqual(self.templates, expected_templates)

    # If a message does not contain a json custom message, it appears as {} in the list
    def assert_json_messages(self, expected_messages: List[Dict[str, Any]]) -> None:
        self.assertEqual(self.json_messages, expected_messages)

    # If a message does not contain a text message, it appears as None in the list
    def assert_texts(self, expected_texts: List[Dict[str, Any]]) -> None:
        self.assertEqual(self.texts, expected_texts)

    # If a message does not contain an attachment, it appears as None in the list
    def assert_attachments(self, expected_attachments: List[Dict[str, Any]]) -> None:
        self.assertEqual(self.attachments, expected_attachments)
