from unittest.mock import MagicMock, patch

from rasa_sdk.events import Form, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.answers import QuestionAnsweringResponse, QuestionAnsweringStatus
from covidflow.actions.constants import (
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
from covidflow.actions.question_answering_form import FORM_NAME, QuestionAnsweringForm

from .form_helper import FormTestCase


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


FULL_RESULT_SUCCESS = {
    QA_ASKED_QUESTION_QUESTION_KEY: QUESTION,
    QA_ASKED_QUESTION_ANSWERS_KEY: ANSWERS,
    QA_ASKED_QUESTION_STATUS_KEY: QuestionAnsweringStatus.SUCCESS,
    QA_ASKED_QUESTION_FEEDBACK_KEY: True,
}


class TestQuestionAnsweringForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.form = QuestionAnsweringForm()

    def test_form_activation_first_time_without_qa_samples(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(tracker)

        self.assert_events(
            [Form(FORM_NAME), SlotSet(REQUESTED_SLOT, QA_ACTIVE_QUESTION_SLOT)]
        )

        self.assert_templates(
            [
                "utter_can_help_with_questions",
                "utter_qa_disclaimer",
                "utter_ask_active_question",
            ]
        )

    def test_form_activation_first_time_with_qa_samples(self):
        tracker = self.create_tracker(active_form=False)

        self.run_form(
            tracker, domain={"responses": {"utter_qa_sample_foo": [{"text": "bar"}]}}
        )

        self.assert_events(
            [Form(FORM_NAME), SlotSet(REQUESTED_SLOT, QA_ACTIVE_QUESTION_SLOT)]
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
            slots={QA_ASKED_QUESTION_SLOT: FULL_RESULT_SUCCESS}, active_form=False,
        )

        self.run_form(tracker)

        self.assert_events(
            [Form(FORM_NAME), SlotSet(REQUESTED_SLOT, QA_ACTIVE_QUESTION_SLOT)]
        )

        self.assert_templates(["utter_ask_active_question"])

    @patch("covidflow.actions.question_answering_form.QuestionAnsweringProtocol")
    def test_provide_question_success(self, mock_protocol):
        mock_protocol.return_value.get_response = QuestionAnsweringResponseMock(
            return_value=SUCCESS_RESULT
        )

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: QA_ACTIVE_QUESTION_SLOT}, text=QUESTION
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(QA_ACTIVE_QUESTION_SLOT, QUESTION),
                SlotSet(QA_STATUS_SLOT, QuestionAnsweringStatus.SUCCESS),
                SlotSet(QA_ANSWERS_SLOT, ANSWERS),
                SlotSet(REQUESTED_SLOT, QA_FEEDBACK_SLOT),
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
            slots={REQUESTED_SLOT: QA_ACTIVE_QUESTION_SLOT}, text=QUESTION
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(QA_ACTIVE_QUESTION_SLOT, QUESTION),
                SlotSet(QA_STATUS_SLOT, QuestionAnsweringStatus.FAILURE),
                SlotSet(QA_ANSWERS_SLOT, None),
                SlotSet(QA_ACTIVE_QUESTION_SLOT, None),
                SlotSet(QA_FEEDBACK_SLOT, None),
                SlotSet(
                    QA_ASKED_QUESTION_SLOT,
                    {
                        QA_ASKED_QUESTION_QUESTION_KEY: QUESTION,
                        QA_ASKED_QUESTION_STATUS_KEY: QuestionAnsweringStatus.FAILURE,
                        QA_ASKED_QUESTION_ANSWERS_KEY: None,
                        QA_ASKED_QUESTION_FEEDBACK_KEY: None,
                    },
                ),
                Form(None),
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
            slots={REQUESTED_SLOT: QA_ACTIVE_QUESTION_SLOT}, text=QUESTION
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(QA_ACTIVE_QUESTION_SLOT, QUESTION),
                SlotSet(QA_STATUS_SLOT, QuestionAnsweringStatus.OUT_OF_DISTRIBUTION),
                SlotSet(QA_ANSWERS_SLOT, None),
                SlotSet(QA_ACTIVE_QUESTION_SLOT, None),
                SlotSet(QA_FEEDBACK_SLOT, None),
                SlotSet(
                    QA_ASKED_QUESTION_SLOT,
                    {
                        QA_ASKED_QUESTION_QUESTION_KEY: QUESTION,
                        QA_ASKED_QUESTION_STATUS_KEY: QuestionAnsweringStatus.OUT_OF_DISTRIBUTION,
                        QA_ASKED_QUESTION_ANSWERS_KEY: None,
                        QA_ASKED_QUESTION_FEEDBACK_KEY: None,
                    },
                ),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_cant_answer"])

    def test_provide_feedback_affirm(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: QA_FEEDBACK_SLOT,
                QA_ACTIVE_QUESTION_SLOT: QUESTION,
                QA_ANSWERS_SLOT: ANSWERS,
                QA_STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            },
            intent="affirm",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(QA_FEEDBACK_SLOT, True),
                SlotSet(QA_ACTIVE_QUESTION_SLOT, None),
                SlotSet(QA_FEEDBACK_SLOT, None),
                SlotSet(QA_ASKED_QUESTION_SLOT, FULL_RESULT_SUCCESS),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates([])

    def test_provide_feedback_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: QA_FEEDBACK_SLOT,
                QA_ACTIVE_QUESTION_SLOT: QUESTION,
                QA_ANSWERS_SLOT: ANSWERS,
                QA_STATUS_SLOT: QuestionAnsweringStatus.SUCCESS,
            },
            intent="deny",
        )

        self.run_form(tracker)

        self.assert_events(
            [
                SlotSet(QA_FEEDBACK_SLOT, False),
                SlotSet(QA_ACTIVE_QUESTION_SLOT, None),
                SlotSet(QA_FEEDBACK_SLOT, None),
                SlotSet(
                    QA_ASKED_QUESTION_SLOT,
                    {**FULL_RESULT_SUCCESS, QA_ASKED_QUESTION_FEEDBACK_KEY: False},
                ),
                Form(None),
                SlotSet(REQUESTED_SLOT, None),
            ]
        )

        self.assert_templates(["utter_post_feedback"])
