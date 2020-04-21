import os
from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.answers import (
    QuestionAnsweringProtocol,
    QuestionAnsweringResponse,
    QuestionAnsweringStatus,
)

FAQ_URL_ENV_KEY = "COVID_FAQ_SERVICE_URL"
DEFAULT_FAQ_URL = "https://covidfaq.dialoguecorp.com"

QUESTION_SLOT = "active_question"
FEEDBACK_SLOT = "feedback"
STATUS_SLOT = "question_answering_status"
ANSWERS_SLOT = "answers"
ASKED_QUESTION_SLOT = "asked_question"


class QuestionAnsweringForm(FormAction):
    def name(self) -> Text:

        return "question_answering_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        status = tracker.get_slot(STATUS_SLOT)
        if status == QuestionAnsweringStatus.SUCCESS:
            return [QUESTION_SLOT, FEEDBACK_SLOT]

        return [QUESTION_SLOT]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            QUESTION_SLOT: self.from_text(),
            FEEDBACK_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
        }

    def validate_active_question(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        protocol = QuestionAnsweringProtocol(
            os.environ.get(FAQ_URL_ENV_KEY, DEFAULT_FAQ_URL)
        )
        result: QuestionAnsweringResponse = protocol.get_response(value)

        if result.status == QuestionAnsweringStatus.OUT_OF_DISTRIBUTION:
            full_result = {
                "question": value,
                "status": result.status,
            }
            dispatcher.utter_message(template="utter_cant_answer")

            return {
                ASKED_QUESTION_SLOT: full_result,
                QUESTION_SLOT: None,
                STATUS_SLOT: None,
            }

        if result.status == QuestionAnsweringStatus.SUCCESS and result.answers:
            dispatcher.utter_message(result.answers[0])

        return {STATUS_SLOT: result.status, ANSWERS_SLOT: result.answers}

    def validate_feedback(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if not value:
            dispatcher.utter_message(template="utter_post_feedback")

        return {FEEDBACK_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        full_question_result = {
            "question": tracker.get_slot(QUESTION_SLOT),
            "answers": tracker.get_slot(ANSWERS_SLOT),
            "status": tracker.get_slot(STATUS_SLOT),
            "feedback": tracker.get_slot(FEEDBACK_SLOT),
        }

        # Clearing and saving in case of re-rentry in the form.
        return [
            SlotSet(QUESTION_SLOT),
            SlotSet(FEEDBACK_SLOT),
            SlotSet(ASKED_QUESTION_SLOT, full_question_result),
        ]
