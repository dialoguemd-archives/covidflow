from unittest import TestCase

from covidflow.db.assessment import (
    FEEL_WORSE_SLOT,
    HAS_COUGH_SLOT,
    HAS_DIFF_BREATHING_SLOT,
    HAS_FEVER_SLOT,
    SYMPTOMS_SLOT,
    Assessment,
)

SYMPTOMS = "tickles"
FEEL_WORSE = True
HAS_COUGH = False
HAS_DIFF_BREATHING = True
HAS_FEVER = False


class TestAssessment(TestCase):
    def test_create_from_slot_values(self):
        assessment = Assessment.create_from_slot_values(
            1,
            {
                SYMPTOMS_SLOT: SYMPTOMS,
                FEEL_WORSE_SLOT: FEEL_WORSE,
                HAS_COUGH_SLOT: HAS_COUGH,
                HAS_DIFF_BREATHING_SLOT: HAS_DIFF_BREATHING,
                HAS_FEVER_SLOT: HAS_FEVER,
                "ignored_slot": "value",
            },
        )
        expected_assessment = Assessment(1)
        expected_assessment.symptoms = SYMPTOMS
        expected_assessment.feel_worse = FEEL_WORSE
        expected_assessment.has_cough = HAS_COUGH
        expected_assessment.has_diff_breathing = HAS_DIFF_BREATHING
        expected_assessment.has_fever = HAS_FEVER

        self.assertEqual(assessment, expected_assessment)
