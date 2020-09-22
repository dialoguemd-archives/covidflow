import os
import random
from typing import Any, Dict, List, Text

import structlog
from aiohttp import ClientSession
from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, BotUttered, EventType, SlotSet, UserUttered
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.constants import (
    ACTION_LISTEN_NAME,
    LANGUAGE_SLOT,
    QA_TEST_PROFILE_ATTRIBUTE,
    SKIP_SLOT_PLACEHOLDER,
)

from .answers import (
    QuestionAnsweringProtocol,
    QuestionAnsweringResponse,
    QuestionAnsweringStatus,
)
from .lib.form_helper import _form_slots_to_validate
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
ASK_QUESTION_ACTION_NAME = f"action_ask_{QUESTION_SLOT}"
VALIDATE_ACTION_NAME = f"validate_{FORM_NAME}"
SUBMIT_ACTION_NAME = f"action_submit_question_answering_form"
FALLBACK_ACTIVATE_ACTION_NAME = "action_activate_fallback_question_answering_form"

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


class ActionActivateFallbackQuestionAnswering(Action):
    def name(self) -> Text:
        return FALLBACK_ACTIVATE_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        question = tracker.latest_message.get("text", "")

        # Slot will be validated on form activation
        return [SlotSet(QUESTION_SLOT, question)]


class ActionAskActiveQuestion(Action):
    def name(self) -> Text:
        return ASK_QUESTION_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        events = []

        if not (tracker.get_slot(SKIP_QA_INTRO_SLOT) is True):

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
            events = [SlotSet(SKIP_QA_INTRO_SLOT, True)]

        dispatcher.utter_message(template="utter_ask_active_question")
        return events


class ValidateQuestionAnsweringForm(Action):
    def name(self) -> Text:
        return VALIDATE_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

        extracted_slots: Dict[Text, Any] = _form_slots_to_validate(tracker)

        validation_events: List[EventType] = []

        for slot_name, slot_value in extracted_slots.items():
            slot_events = [SlotSet(slot_name, slot_value)]

            if slot_name == FEEDBACK_SLOT:
                if slot_value is False:
                    dispatcher.utter_message(template="utter_feedback_false")
                elif not isinstance(slot_value, bool):
                    slot_events = [SlotSet(FEEDBACK_SLOT, FEEDBACK_NOT_GIVEN)]
            elif slot_name == QUESTION_SLOT:
                result = (
                    _get_stub_qa_result(tracker)
                    if _must_stub_result(tracker)
                    else await _fetch_qa(slot_value, tracker)
                )

                slot_events += [SlotSet(STATUS_SLOT, result.status)]

                if result.status == QuestionAnsweringStatus.SUCCESS:
                    dispatcher.utter_message(result.answers[0])
                    slot_events += [SlotSet(ANSWERS_SLOT, result.answers)]
                else:
                    slot_events += [
                        SlotSet(REQUESTED_SLOT, None),
                        SlotSet(FEEDBACK_SLOT, SKIP_SLOT_PLACEHOLDER),
                    ]

            validation_events.extend(slot_events)

        return validation_events


class ActionSubmitQuestionAnsweringForm(Action):
    def name(self) -> Text:
        return SUBMIT_ACTION_NAME

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        bind_logger(tracker)

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


def _carry_user_utterance(tracker: Tracker) -> List[EventType]:
    return [
        ActionExecuted("utter_ask_another_question"),
        BotUttered(metadata={"template_name": "utter_ask_another_question"}),
        ActionExecuted(ACTION_LISTEN_NAME),
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
