import unittest

from rasa_sdk import Tracker
from rasa_sdk.events import Restarted
from rasa_sdk.executor import CollectingDispatcher

from covidflow.actions.action_send_validation_code import ActionSendValidationCode
from covidflow.constants import ACTION_LISTEN_NAME
from covidflow.utils.phone_number_validation import (
    FIRST_NAME_ENTITY,
    VALIDATION_CODE_ENTITY,
)


class ActionSendValidationCodeTest(unittest.TestCase):
    def test_action_name(self):
        assert ActionSendValidationCode().name() == "action_send_validation_code"

    def test_send_validation_code(self):
        first_name = "Bob"
        validation_code = "1234"

        entities = [
            {"entity": FIRST_NAME_ENTITY, "value": first_name},
            {"entity": VALIDATION_CODE_ENTITY, "value": validation_code},
        ]

        tracker = Tracker(
            "default",
            {},
            {"entities": entities},
            [],
            False,
            None,
            {},
            ACTION_LISTEN_NAME,
        )

        dispatcher = CollectingDispatcher()
        events = ActionSendValidationCode().run(dispatcher, tracker, {})

        self.assertListEqual(events, [Restarted()])
        self.assertListEqual(
            dispatcher.messages,
            [
                {
                    "attachment": None,
                    "buttons": [],
                    "custom": {},
                    "elements": [],
                    "first_name": first_name,
                    "image": None,
                    "template": "utter_daily_checkin_validation_code",
                    "text": None,
                    "validation_code": validation_code,
                }
            ],
        )
