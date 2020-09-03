from typing import Any, Dict, List

from rasa_sdk import Tracker
from rasa_sdk.events import ActionExecuted, SlotSet

from .action_test_helper import ActionTestCase


class ValidateActionTestCase(ActionTestCase):
    def setUp(self):
        self.form_name: str = None
        super().setUp()

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
        active_loop: bool = True,
        last_action: str = "action_listen",
    ) -> Tracker:
        return Tracker(
            sender_id,
            slots,
            {
                "intent": {"name": intent or "none"},
                "entities": entities or [],
                "text": text or "",
            },
            events or [],
            paused,
            followup_action,
            {"name": self.form_name, "validate": True, "rejected": False}
            if active_loop
            else {},
            last_action,
        )

    def check_slot_value_accepted(self, slot_name: str, value: Any) -> None:
        self.check_slot_value_stored(slot_name, value, value)

    def check_slot_value_rejected(self, slot_name: str, value: Any) -> None:
        self.check_slot_value_stored(slot_name, value, None)

    def check_slot_value_stored(
        self, slot_name: str, extracted_value: Any, stored_value: Any
    ) -> None:
        tracker = self.create_tracker(
            events=[ActionExecuted(self.form_name), SlotSet(slot_name, extracted_value)]
        )

        self.run_action(tracker)

        self.assert_events([SlotSet(slot_name, stored_value)])
