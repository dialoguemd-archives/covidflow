import os
import random
from typing import Any, Dict, List, Text, Union

from aiohttp import ClientSession
from rasa_sdk import Tracker
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from .answers import (
    QuestionAnsweringProtocol,
    QuestionAnsweringResponse,
    QuestionAnsweringStatus,
)
from .constants import LANGUAGE_SLOT, QA_TEST_PROFILE_ATTRIBUTE
from .lib.log_util import bind_logger

FAQ_URL_ENV_KEY = "COVID_FAQ_SERVICE_URL"
DEFAULT_FAQ_URL = "https://covidfaq.dialoguecorp.com"

QUESTION_SLOT = "active_question"
FEEDBACK_SLOT = "feedback"
STATUS_SLOT = "question_answering_status"
ANSWERS_SLOT = "answers"
ASKED_QUESTION_SLOT = "asked_question"

ANSWERS_KEY = "answers"
STATUS_KEY = "status"
FEEDBACK_KEY = "feedback"
QUESTION_KEY = "question"

FORM_NAME = "question_answering_form"

TEST_PROFILES_RESPONSE = {
    "success": QuestionAnsweringResponse(
        answers=["this is my answer"], status=QuestionAnsweringStatus.SUCCESS
    ),
    "failure": QuestionAnsweringResponse(status=QuestionAnsweringStatus.FAILURE),
    "need_assessment": QuestionAnsweringResponse(
        status=QuestionAnsweringStatus.NEED_ASSESSMENT
    ),
    "out_of_distribution": QuestionAnsweringResponse(
        status=QuestionAnsweringStatus.OUT_OF_DISTRIBUTION
    ),
}


class QuestionAnsweringForm(FormAction):
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
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        # Messages are only played for the first question
        if (
            tracker.active_form.get("name") != FORM_NAME
            and tracker.get_slot(ASKED_QUESTION_SLOT) is None
        ):
            dispatcher.utter_message(template="utter_can_help_with_questions")
            dispatcher.utter_message(template="utter_qa_disclaimer")

            random_qa_samples = (
                _get_fixed_questions_samples()
                if _must_stub_result(tracker)
                else _get_random_question_samples(domain)
            )

            if len(random_qa_samples) > 0:
                dispatcher.utter_message(
                    template="utter_qa_sample",
                    sample_questions="\n".join(random_qa_samples),
                )
        return await super()._activate_if_required(dispatcher, tracker, domain)

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

    async def validate_active_question(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if _must_stub_result(tracker):
            result = _get_stub_qa_result(tracker)
        else:
            result = await _fetch_qa(value, tracker)

        if result.status == QuestionAnsweringStatus.OUT_OF_DISTRIBUTION:
            dispatcher.utter_message(template="utter_cant_answer")

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
            QUESTION_KEY: tracker.get_slot(QUESTION_SLOT),
            ANSWERS_KEY: tracker.get_slot(ANSWERS_SLOT),
            STATUS_KEY: tracker.get_slot(STATUS_SLOT),
            FEEDBACK_KEY: tracker.get_slot(FEEDBACK_SLOT),
        }

        # Clearing and saving in case of re-rentry in the form.
        return [
            SlotSet(QUESTION_SLOT),
            SlotSet(FEEDBACK_SLOT),
            SlotSet(ASKED_QUESTION_SLOT, full_question_result),
        ]


def _must_stub_result(tracker: Tracker):
    metadata = tracker.get_slot("metadata") or {}
    return QA_TEST_PROFILE_ATTRIBUTE in metadata


def _get_random_question_samples(domain: Dict[Text, Any],) -> List[str]:
    responses = domain.get("responses", {})
    qa_samples_categories = [
        key for key in responses.keys() if key.startswith("utter_qa_sample_")
    ]
    random_qa_samples_categories = random.sample(
        qa_samples_categories, k=min(len(qa_samples_categories), 3)
    )

    return [
        f"- {random.choice(value).get('text')}"
        for key, value in responses.items()
        if key in random_qa_samples_categories
    ]


def _get_fixed_questions_samples() -> List[str]:
    return ["- sample question 1", "- sample question 2"]


async def _fetch_qa(text: Text, tracker: Tracker) -> QuestionAnsweringResponse:
    protocol = QuestionAnsweringProtocol(
        os.environ.get(FAQ_URL_ENV_KEY, DEFAULT_FAQ_URL)
    )

    language = tracker.get_slot(LANGUAGE_SLOT)
    async with ClientSession() as session:
        return await protocol.get_response(session, text, language)


def _get_stub_qa_result(tracker: Tracker):
    profile = tracker.get_slot("metadata")[QA_TEST_PROFILE_ATTRIBUTE]
    return TEST_PROFILES_RESPONSE[profile]
