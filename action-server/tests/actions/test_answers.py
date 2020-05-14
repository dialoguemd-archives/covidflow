from unittest import TestCase

from covidflow.actions.answers import format_answers


class QaAnswersTest(TestCase):
    def test_answer_format(self):
        formatted_answers = format_answers(["<strong>This is not bold.</strong>\nLine"])
        self.assertEqual(formatted_answers[0], "This is not bold.\nLine")

    def test_none_format(self):
        self.assertIsNone(format_answers(None))

    def test_multiline_tags(self):
        formatted_answers = format_answers(["Three < One\n> Quote"])
        self.assertEqual(formatted_answers[0], "Three < One\n> Quote")
