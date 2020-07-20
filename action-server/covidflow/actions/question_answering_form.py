import os
import random
from typing import Any, Dict, List, Optional, Text, Union

import structlog
from aiohttp import ClientSession
from rasa_sdk import Tracker
from rasa_sdk.events import ActionExecuted, EventType, Form, SlotSet, UserUttered
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT, FormAction

from covidflow.constants import LANGUAGE_SLOT, QA_TEST_PROFILE_ATTRIBUTE

from .answers import (
    QuestionAnsweringProtocol,
    QuestionAnsweringResponse,
    QuestionAnsweringStatus,
)
from .form_helper import request_next_slot, yes_no_nlu_mapping
from .lib.log_util import bind_logger

logger = structlog.get_logger()

FAQ_URL_ENV_KEY = "COVID_FAQ_SERVICE_URL"
DEFAULT_FAQ_URL = "https://covidfaq.dialoguecorp.com"

QUESTION_SLOT = "active_question"
FEEDBACK_SLOT = "feedback"
STATUS_SLOT = "question_answering_status"
ANSWERS_SLOT = "answers"
ASKED_QUESTION_SLOT = "asked_question"
SKIP_QA_INTRO_SLOT = "skip_qa_intro"

ANSWERS_KEY = "answers"
STATUS_KEY = "status"
FEEDBACK_KEY = "feedback"
QUESTION_KEY = "question"

FEEDBACK_NOT_GIVEN = "not_given"

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

    ## override to play initial messages or prefill slots
    async def _activate_if_required(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:
        if tracker.active_form.get("name") == FORM_NAME:
            return await super()._activate_if_required(dispatcher, tracker, domain)

        intent = _get_intent(tracker)

        # Fallback QA
        if intent == "nlu_fallback":
            question = tracker.latest_message.get("text", "")

            result = await self.validate_active_question(
                question, dispatcher, tracker, domain
            )

            return await super()._activate_if_required(dispatcher, tracker, domain) + [
                SlotSet(QUESTION_SLOT, question),
                SlotSet(STATUS_SLOT, result[STATUS_SLOT]),
                SlotSet(ANSWERS_SLOT, result[ANSWERS_SLOT]),
            ]

        # Regular QA
        # Messages are only played for the first question
        if tracker.get_slot(SKIP_QA_INTRO_SLOT) == True or intent != "ask_question":
            return await super()._activate_if_required(dispatcher, tracker, domain)

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

        return await super()._activate_if_required(dispatcher, tracker, domain) + [
            SlotSet(SKIP_QA_INTRO_SLOT, True)
        ]

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        status = tracker.get_slot(STATUS_SLOT)
        if status == QuestionAnsweringStatus.SUCCESS:
            return [QUESTION_SLOT, FEEDBACK_SLOT]

        return [QUESTION_SLOT]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            QUESTION_SLOT: self.from_text(),
            FEEDBACK_SLOT: yes_no_nlu_mapping(self),
        }

    def request_next_slot(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:
        return request_next_slot(self, dispatcher, tracker, domain)

    async def validate_active_question(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        result = (
            _get_stub_qa_result(tracker)
            if _must_stub_result(tracker)
            else await _fetch_qa(value, tracker)
        )

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
        if value is False:
            dispatcher.utter_message(template="utter_post_feedback")

        if not isinstance(value, bool):
            return {FEEDBACK_SLOT: FEEDBACK_NOT_GIVEN}

        return {}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        feedback = tracker.get_slot(FEEDBACK_SLOT)
        full_question_result = {
            QUESTION_KEY: tracker.get_slot(QUESTION_SLOT),
            ANSWERS_KEY: tracker.get_slot(ANSWERS_SLOT),
            STATUS_KEY: tracker.get_slot(STATUS_SLOT),
            FEEDBACK_KEY: feedback,
        }

        # Clearing and saving in case of re-rentry in the form.
        slot_sets = [
            SlotSet(QUESTION_SLOT),
            SlotSet(FEEDBACK_SLOT),
            SlotSet(ASKED_QUESTION_SLOT, full_question_result),
        ]

        if feedback == FEEDBACK_NOT_GIVEN:
            return slot_sets + _carry_user_utterance(tracker)

        return slot_sets


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


def _get_intent(tracker: Tracker) -> str:
    return tracker.latest_message.get("intent", {}).get("name", "")


def _carry_user_utterance(tracker: Tracker) -> List[EventType]:
    return [
        Form(None),  # Ending it manually to have events in correct order to fit stories
        SlotSet(REQUESTED_SLOT, None),
        ActionExecuted("utter_ask_another_question"),
        ActionExecuted("action_listen"),
        UserUttered(
            tracker.latest_message.get("text", ""),
            parse_data={
                "text": tracker.latest_message.get("text", ""),
                "intent": tracker.latest_message.get("intent", {}),
                "intent_ranking": tracker.latest_message.get("intent_ranking", []),
                "entities": tracker.latest_message.get("entities", []),
            },
        ),
    ]
