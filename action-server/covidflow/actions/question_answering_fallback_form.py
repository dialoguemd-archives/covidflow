import os
from typing import Any, Dict, List, Text, Union

from aiohttp import ClientSession
from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .answers import (
    DEFAULT_FAQ_URL,
    FAQ_URL_ENV_KEY,
    QuestionAnsweringProtocol,
    QuestionAnsweringResponse,
    QuestionAnsweringStatus,
)
from .constants import (
    LANGUAGE_SLOT,
    QA_ACTIVE_QUESTION_SLOT,
    QA_ANSWERS_SLOT,
    QA_ASKED_QUESTION_ANSWERS_KEY,
    QA_ASKED_QUESTION_FEEDBACK_KEY,
    QA_ASKED_QUESTION_QUESTION_KEY,
    QA_ASKED_QUESTION_SLOT,
    QA_ASKED_QUESTION_STATUS_KEY,
    QA_FEEDBACK_SLOT,
    QA_STATUS_SLOT,
)
from .lib.log_util import bind_logger

FORM_NAME = "question_answering_fallback_form"


class QuestionAnsweringFallbackForm(FormAction):
    def name(self) -> Text:

        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

    ## override to play initial messages
    async def _activate_if_required(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_form.get("name") != FORM_NAME:
            question = tracker.latest_message.get("text", "")

            protocol = QuestionAnsweringProtocol(
                os.environ.get(FAQ_URL_ENV_KEY, DEFAULT_FAQ_URL)
            )

            language = tracker.get_slot(LANGUAGE_SLOT)
            async with ClientSession() as session:
                result: QuestionAnsweringResponse = await protocol.get_response(
                    session, question, language
                )

                if result.status == QuestionAnsweringStatus.SUCCESS and result.answers:
                    dispatcher.utter_message(result.answers[0])

                return await super()._activate_if_required(
                    dispatcher, tracker, domain
                ) + [
                    SlotSet(QA_ACTIVE_QUESTION_SLOT, question),
                    SlotSet(QA_STATUS_SLOT, result.status),
                    SlotSet(QA_ANSWERS_SLOT, result.answers),
                ]

        return await super()._activate_if_required(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        status = tracker.get_slot(QA_STATUS_SLOT)
        if status == QuestionAnsweringStatus.SUCCESS:
            return [QA_FEEDBACK_SLOT]

        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            QA_FEEDBACK_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
        }

    def validate_feedback(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if not value:
            dispatcher.utter_message(template="utter_post_feedback")

        return {QA_FEEDBACK_SLOT: value}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        full_question_result = {
            QA_ASKED_QUESTION_QUESTION_KEY: tracker.get_slot(QA_ACTIVE_QUESTION_SLOT),
            QA_ASKED_QUESTION_ANSWERS_KEY: tracker.get_slot(QA_ANSWERS_SLOT),
            QA_ASKED_QUESTION_STATUS_KEY: tracker.get_slot(QA_STATUS_SLOT),
            QA_ASKED_QUESTION_FEEDBACK_KEY: tracker.get_slot(QA_FEEDBACK_SLOT),
        }

        # Clearing and saving in case of re-rentry in the form.
        return [
            SlotSet(QA_ACTIVE_QUESTION_SLOT),
            SlotSet(QA_FEEDBACK_SLOT),
            SlotSet(QA_ASKED_QUESTION_SLOT, full_question_result),
        ]
