class Symptoms:  # Not using an enum to avoid persisting enum values
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


PROVINCES_WITH_211 = ["bc", "ab", "sk", "mb", "on", "qc", "ns"]

END_CONVERSATION_MESSAGE = {"data": {"endOfConversation": True}}

# Slots

## Slots used by DB
METADATA_SLOT = "metadata"

### Last assessment
LAST_SYMPTOMS_SLOT = "last_symptoms"
LAST_HAS_FEVER_SLOT = "last_has_fever"
LAST_HAS_COUGH_SLOT = "last_has_cough"
LAST_HAS_DIFF_BREATHING_SLOT = "last_has_diff_breathing"

LAST_ASSESSMENT_SLOTS = [
    LAST_SYMPTOMS_SLOT,
    LAST_HAS_FEVER_SLOT,
    LAST_HAS_COUGH_SLOT,
    LAST_HAS_DIFF_BREATHING_SLOT,
]

### Assessment
FEEL_WORSE_SLOT = "feel_worse"
SYMPTOMS_SLOT = "symptoms"
HAS_FEVER_SLOT = "has_fever"
HAS_COUGH_SLOT = "has_cough"
HAS_DIFF_BREATHING_SLOT = "has_diff_breathing"

### Profile
LANGUAGE_SLOT = "language"
FIRST_NAME_SLOT = "first_name"
PHONE_NUMBER_SLOT = "phone_number"
PRECONDITIONS_SLOT = "preconditions"
HAS_DIALOGUE_SLOT = "has_dialogue"
PROVINCE_SLOT = "province"
AGE_OVER_65_SLOT = "age_over_65"

## Slots used only in flows
CANCEL_CI_SLOT = "cancel_ci"
HAS_ASSISTANCE_SLOT = "has_assistance"
LIVES_ALONE_SLOT = "lives_alone"
PROVINCIAL_811_SLOT = "provincial_811"  # used for interpolation
SELF_ASSESS_DONE_SLOT = "self_assess_done"
SEVERE_SYMPTOMS_SLOT = "severe_symptoms"
MODERATE_SYMPTOMS_SLOT = "moderate_symptoms"
CONTACT_SLOT = "contact"
TRAVEL_SLOT = "travel"
HAS_CONTACT_RISK_SLOT = "has_contact_risk"

QA_ACTIVE_QUESTION_SLOT = "active_question"
QA_FEEDBACK_SLOT = "feedback"
QA_ANSWERS_SLOT = "answers"
QA_ASKED_QUESTION_SLOT = "asked_question"

# Shared with stories
INVALID_REMINDER_ID_SLOT = "invalid_reminder_id"
QA_STATUS_SLOT = "question_answering_status"

# Slot values
QA_ASKED_QUESTION_ANSWERS_KEY = "answers"
QA_ASKED_QUESTION_STATUS_KEY = "status"
QA_ASKED_QUESTION_FEEDBACK_KEY = "feedback"
QA_ASKED_QUESTION_QUESTION_KEY = "question"
