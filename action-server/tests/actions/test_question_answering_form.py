import pytest
from asynctest.mock import MagicMock, patch
from rasa_sdk.events import ActionExecuted, BotUttered, SlotSet, UserUttered
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
    SKIP_SLOT_PLACEHOLDER,
    STATUS_KEY,
    STATUS_SLOT,
    ActionActivateFallbackQuestionAnswering,
    ActionAskActiveQuestion,
    ActionSubmitQuestionAnsweringForm,
    ValidateQuestionAnsweringForm,
)
from covidflow.constants import ACTION_LISTEN_NAME

from .action_test_helper import ActionTestCase
from .validate_action_test_helper import ValidateActionTestCase


def QuestionAnsweringResponseMock(*args, **kwargs):
    mock = MagicMock(*args, **kwargs)

    async def mock_coroutine(*args, **kwargs):
        return mock(*args, **kwargs)

    mock_coroutine.mock = mock
    return mock_coroutine


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


class TestActionActivateFallbackQuestionAnswering(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionActivateFallbackQuestionAnswering()

    @pytest.mark.asyncio
    async def test_fills_active_question(self):
        tracker = self.create_tracker(text="I asked my question in advance")

        await self.run_action(tracker)

        self.assert_events([SlotSet(QUESTION_SLOT, "I asked my question in advance")])

        self.assert_templates([])


class TestActionAskActiveQuestion(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionAskActiveQuestion()

    @pytest.mark.asyncio
    async def test_first_time_without_qa_samples(self):
        tracker = self.create_tracker(intent="ask_question")

        await self.run_action(tracker)

        self.assert_events([SlotSet(SKIP_QA_INTRO_SLOT, True)])

        self.assert_templates(
            [
                "utter_can_help_with_questions",
                "utter_qa_disclaimer",
                "utter_ask_active_question",
            ]
        )

    @pytest.mark.asyncio
    async def test_first_time_with_qa_samples(self):
        tracker = self.create_tracker(intent="ask_question")

        await self.run_action(
            tracker, domain={"responses": {"utter_qa_sample_foo": [{"text": "bar"}]}}
        )

        self.assert_events([SlotSet(SKIP_QA_INTRO_SLOT, True)])

        self.assert_templates(
            [
                "utter_can_help_with_questions",
                "utter_qa_disclaimer",
                "utter_qa_sample",
                "utter_ask_active_question",
            ]
        )

    @pytest.mark.asyncio
    async def test_not_first_time(self):
        tracker = self.create_tracker(
            slots={ASKED_QUESTION_SLOT: FULL_RESULT_SUCCESS, SKIP_QA_INTRO_SLOT: True},
            intent="ask_question",
        )

        await self.run_action(tracker)

        self.assert_events([])

        self.assert_templates(["utter_ask_active_question"])


class TestValidateQuestionAnsweringForm(ValidateActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ValidateQuestionAnsweringForm()
        self.form_name = FORM_NAME

    @pytest.mark.asyncio
    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    async def test_provide_question_success(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=SUCCESS_RESULT
        )

        extra_events = [
            SlotSet(STATUS_SLOT, QuestionAnsweringStatus.SUCCESS),
            SlotSet(ANSWERS_SLOT, ANSWERS),
        ]

        templates = [None]

        await self.check_slot_value_accepted(
            QUESTION_SLOT, QUESTION, extra_events=extra_events, templates=templates
        )

        self.assert_texts([ANSWERS[0]])

    @pytest.mark.asyncio
    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    async def test_provide_question_failure(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=FAILURE_RESULT
        )

        extra_events = [
            SlotSet(STATUS_SLOT, QuestionAnsweringStatus.FAILURE),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(FEEDBACK_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            QUESTION_SLOT, QUESTION, extra_events=extra_events
        )

    @pytest.mark.asyncio
    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    async def test_provide_question_out_of_distribution(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=OUT_OF_DISTRIBUTION_RESULT
        )

        extra_events = [
            SlotSet(STATUS_SLOT, QuestionAnsweringStatus.OUT_OF_DISTRIBUTION),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(FEEDBACK_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            QUESTION_SLOT, QUESTION, extra_events=extra_events
        )

    @pytest.mark.asyncio
    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    async def test_fallback_question_need_assessment(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=NEED_ASSESSMENT_RESULT
        )

        extra_events = [
            SlotSet(STATUS_SLOT, QuestionAnsweringStatus.NEED_ASSESSMENT),
            SlotSet(REQUESTED_SLOT, None),
            SlotSet(FEEDBACK_SLOT, SKIP_SLOT_PLACEHOLDER),
        ]

        await self.check_slot_value_accepted(
            QUESTION_SLOT, QUESTION, extra_events=extra_events
        )

    @pytest.mark.asyncio
    async def test_provide_feedback_affirm(self):
        await self.check_slot_value_accepted(FEEDBACK_SLOT, True)

    @pytest.mark.asyncio
    async def test_provide_feedback_deny(self):
        templates = ["utter_feedback_false"]
        await self.check_slot_value_accepted(FEEDBACK_SLOT, False, templates=templates)

    @pytest.mark.asyncio
    async def test_provide_feedback_not_given(self):
        await self.check_slot_value_stored(
            FEEDBACK_SLOT, "anything else", FEEDBACK_NOT_GIVEN
        )


class TestActionSubmitQuestionAnsweringForm(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionSubmitQuestionAnsweringForm()

    @pytest.mark.asyncio
    async def test_submit_success(self):
        tracker = self.create_tracker(
            slots={
                QUESTION_SLOT: QUESTION,
                FEEDBACK_SLOT: False,
                ANSWERS_SLOT: ANSWERS,
                STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            }
        )

        await self.run_action(tracker)

        self.assert_events(
            [
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {
                        QUESTION_KEY: QUESTION,
                        STATUS_KEY: QuestionAnsweringStatus.SUCCESS,
                        ANSWERS_KEY: ANSWERS,
                        FEEDBACK_KEY: False,
                    },
                ),
            ]
        )

        self.assert_templates([])

    @pytest.mark.asyncio
    async def test_submit_feedback_not_given(self):
        tracker = self.create_tracker(
            slots={
                QUESTION_SLOT: QUESTION,
                FEEDBACK_SLOT: FEEDBACK_NOT_GIVEN,
                ANSWERS_SLOT: ANSWERS,
                STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            },
            text="some text with",
            intent="another_intent",
            entities=[{"and": "entities"}],
        )

        await self.run_action(tracker)

        self.assert_events(
            [
                SlotSet(QUESTION_SLOT, None),
                SlotSet(FEEDBACK_SLOT, None),
                SlotSet(
                    ASKED_QUESTION_SLOT,
                    {**FULL_RESULT_SUCCESS, FEEDBACK_KEY: FEEDBACK_NOT_GIVEN},
                ),
                ActionExecuted("utter_ask_another_question"),
                BotUttered(metadata={"template_name": "utter_ask_another_question"}),
                ActionExecuted(ACTION_LISTEN_NAME),
                UserUttered(
                    "some text with",
                    parse_data={
                        "text": "some text with",
                        "intent": {"name": "another_intent"},
                        "intent_ranking": [],
                        "entities": [{"and": "entities"}],
                    },
                ),
            ]
        )

        self.assert_templates([])

    @pytest.mark.asyncio
    async def test_submit_failure(self):
        tracker = self.create_tracker(
            slots={
                QUESTION_SLOT: QUESTION,
                STATUS_SLOT: QuestionAnsweringStatus.FAILURE,
            }
        )

        await self.run_action(tracker)

        self.assert_events(
            [
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
            ]
        )

        self.assert_templates([])

    @pytest.mark.asyncio
    async def test_submit_out_of_distribution(self):
        tracker = self.create_tracker(
            slots={
                QUESTION_SLOT: QUESTION,
                STATUS_SLOT: QuestionAnsweringStatus.OUT_OF_DISTRIBUTION,
            }
        )

        await self.run_action(tracker)

        self.assert_events(
            [
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
            ]
        )

        self.assert_templates([])

    @pytest.mark.asyncio
    async def test_submit_need_assessment(self):
        tracker = self.create_tracker(
            slots={
                QUESTION_SLOT: QUESTION,
                STATUS_SLOT: QuestionAnsweringStatus.NEED_ASSESSMENT,
            }
        )

        await self.run_action(tracker)

        self.assert_events(
            [
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
            ]
        )

        self.assert_templates([])
