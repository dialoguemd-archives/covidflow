from unittest.mock import MagicMock, patch

from rasa_sdk.events import ActionExecuted, ActiveLoop, SlotSet, UserUttered
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.answers import QuestionAnsweringResponse, QuestionAnsweringStatus
from covidflow.actions.question_answering_form import (
    ANSWERS_KEY,
    ANSWERS_SLOT,
    ASKED_QUESTION_SLOT,
    FEEDBACK_KEY,
    FEEDBACK_NOT_GIVEN,
    FEEDBACK_SLOT,
    FORM_NAME,
    QUESTION_KEY,
    QUESTION_SLOT,
    SKIP_QA_INTRO_SLOT,
    STATUS_KEY,
    STATUS_SLOT,
    QuestionAnsweringForm,
)

from .form_test_helper import FormTestCase


def QuestionAnsweringResponseMock(*args, **kwargs):
    mock = MagicMock(*args, **kwargs)

    async def mock_coroutine(*args, **kwargs):
        return mock(*args, **kwargs)

    mock_coroutine.mock = mock
    return mock_coroutine


DOMAIN = {"responses": {"utter_ask_feedback_error": [{"text": ""}],}}

QUESTION = "What is covid?"
ANSWERS = [
    "It's a virus!",
    "It's the greatest plea since the plague!",
    "No, it's SU-PER BAD!",
]

SUCCESS_RESULT = QuestionAnsweringResponse(
    answers=ANSWERS, status=QuestionAnsweringStatus.SUCCESS
)
FAILURE_RESULT = QuestionAnsweringResponse(status=QuestionAnsweringStatus.FAILURE)
OUT_OF_DISTRIBUTION_RESULT = QuestionAnsweringResponse(
    status=QuestionAnsweringStatus.OUT_OF_DISTRIBUTION
)
NEED_ASSESSMENT_RESULT = QuestionAnsweringResponse(
    status=QuestionAnsweringStatus.NEED_ASSESSMENT
)

FULL_RESULT_SUCCESS = {
    QUESTION_KEY: QUESTION,
    ANSWERS_KEY: ANSWERS,
    STATUS_KEY: QuestionAnsweringStatus.SUCCESS,
    FEEDBACK_KEY: True,
}


class TestQuestionAnsweringForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = QuestionAnsweringForm()

    def test_form_activation_first_time_without_qa_samples(self):
        tracker = self.create_tracker(active_loop=False, intent="ask_question")

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(SKIP_QA_INTRO_SLOT, True),
                SlotSet(REQUESTED_SLOT, QUESTION_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_can_help_with_questions",
                "utter_qa_disclaimer",
                "utter_ask_active_question",
            ]
        )

    def test_form_activation_first_time_with_qa_samples(self):
        tracker = self.create_tracker(active_loop=False, intent="ask_question")

        self.run_form(
            tracker, domain={"responses": {"utter_qa_sample_foo": [{"text": "bar"}]}}
        )

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(SKIP_QA_INTRO_SLOT, True),
                SlotSet(REQUESTED_SLOT, QUESTION_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_can_help_with_questions",
                "utter_qa_disclaimer",
                "utter_qa_sample",
                "utter_ask_active_question",
            ]
        )

    def test_form_activation_not_first_time(self):
        tracker = self.create_tracker(
            slots={ASKED_QUESTION_SLOT: FULL_RESULT_SUCCESS, SKIP_QA_INTRO_SLOT: True},
            active_loop=False,
            intent="ask_question",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, QUESTION_SLOT)]
        )

        self.assert_templates(["utter_ask_active_question"])

    def test_form_activation_affirm(self):
        tracker = self.create_tracker(
            slots={ASKED_QUESTION_SLOT: FULL_RESULT_SUCCESS},
            active_loop=False,
            intent="affirm",
            text="What is covid?",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, QUESTION_SLOT)]
        )

        self.assert_templates(["utter_ask_active_question"])

    def test_form_activation_fallback(self):
        tracker = self.create_tracker(
            slots={ASKED_QUESTION_SLOT: FULL_RESULT_SUCCESS, SKIP_QA_INTRO_SLOT: True},
            active_loop=False,
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, QUESTION_SLOT)]
        )

        self.assert_templates(["utter_ask_active_question"])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_provide_question_success(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=SUCCESS_RESULT
        )

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: QUESTION_SLOT}, text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.SUCCESS),
                SlotSet(ANSWERS_SLOT, ANSWERS),
                SlotSet(REQUESTED_SLOT, FEEDBACK_SLOT),
            ]
        )

        self.assert_templates([None, "utter_ask_feedback"])

        self.assert_texts([ANSWERS[0], None])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_provide_question_failure(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=FAILURE_RESULT
        )

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: QUESTION_SLOT}, text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.FAILURE),
                SlotSet(ANSWERS_SLOT, None),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {
                        QUESTION_KEY: QUESTION,
                        STATUS_KEY: QuestionAnsweringStatus.FAILURE,
                        ANSWERS_KEY: None,
                        FEEDBACK_KEY: None,
                    },
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_provide_question_out_of_distribution(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=OUT_OF_DISTRIBUTION_RESULT
        )

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: QUESTION_SLOT}, text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.OUT_OF_DISTRIBUTION),
                SlotSet(ANSWERS_SLOT, None),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {
                        QUESTION_KEY: QUESTION,
                        STATUS_KEY: QuestionAnsweringStatus.OUT_OF_DISTRIBUTION,
                        ANSWERS_KEY: None,
                        FEEDBACK_KEY: None,
                    },
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_provide_feedback_affirm(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: FEEDBACK_SLOT,
                QUESTION_SLOT: QUESTION,
                ANSWERS_SLOT: ANSWERS,
                STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(FEEDBACK_SLOT, True),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(ASKED_QUESTION_SLOT, FULL_RESULT_SUCCESS),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_provide_feedback_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: FEEDBACK_SLOT,
                QUESTION_SLOT: QUESTION,
                ANSWERS_SLOT: ANSWERS,
                STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(FEEDBACK_SLOT, False),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT, {**FULL_RESULT_SUCCESS, FEEDBACK_KEY: False}
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_post_feedback"])

    def test_provide_feedback_not_given(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: FEEDBACK_SLOT,
                QUESTION_SLOT: QUESTION,
                ANSWERS_SLOT: ANSWERS,
                STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            },
            text="some text with",
            intent="another_intent",
            entities=[{"and": "entities"}],
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(FEEDBACK_SLOT, FEEDBACK_NOT_GIVEN),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {**FULL_RESULT_SUCCESS, FEEDBACK_KEY: FEEDBACK_NOT_GIVEN},
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
                ActionExecuted("utter_ask_another_question"),
                ActionExecuted("action_listen"),
                UserUttered(
                    "some text with",
                    parse_data={
                        "text": "some text with",
                        "intent": {"name": "another_intent"},
                        "intent_ranking": [],
                        "entities": [{"and": "entities"}],
                    },
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_fallback_question_success(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=SUCCESS_RESULT
        )

        tracker = self.create_tracker(
            active_loop=False, intent="nlu_fallback", text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.SUCCESS),
                SlotSet(ANSWERS_SLOT, ANSWERS),
                SlotSet(REQUESTED_SLOT, FEEDBACK_SLOT),
            ]
        )

        self.assert_templates([None, "utter_ask_feedback"])

        self.assert_texts([ANSWERS[0], None])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_fallback_question_failure(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=FAILURE_RESULT
        )

        tracker = self.create_tracker(
            active_loop=False, intent="nlu_fallback", text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.FAILURE),
                SlotSet(ANSWERS_SLOT, None),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {
                        QUESTION_KEY: QUESTION,
                        STATUS_KEY: QuestionAnsweringStatus.FAILURE,
                        ANSWERS_KEY: None,
                        FEEDBACK_KEY: None,
                    },
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_fallback_question_out_of_distribution(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=OUT_OF_DISTRIBUTION_RESULT
        )

        tracker = self.create_tracker(
            active_loop=False, intent="nlu_fallback", text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.OUT_OF_DISTRIBUTION),
                SlotSet(ANSWERS_SLOT, None),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {
                        QUESTION_KEY: QUESTION,
                        STATUS_KEY: QuestionAnsweringStatus.OUT_OF_DISTRIBUTION,
                        ANSWERS_KEY: None,
                        FEEDBACK_KEY: None,
                    },
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_fallback_question_need_assessment(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=NEED_ASSESSMENT_RESULT
        )

        tracker = self.create_tracker(
            active_loop=False, intent="nlu_fallback", text=QUESTION
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                ActiveLoop(FORM_NAME),
                SlotSet(QUESTION_SLOT, QUESTION),
                SlotSet(STATUS_SLOT, QuestionAnsweringStatus.NEED_ASSESSMENT),
                SlotSet(ANSWERS_SLOT, None),
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {
                        QUESTION_KEY: QUESTION,
                        STATUS_KEY: QuestionAnsweringStatus.NEED_ASSESSMENT,
                        ANSWERS_KEY: None,
                        FEEDBACK_KEY: None,
                    },
                ),
                ActiveLoop(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])
