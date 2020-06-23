import sys
from pathlib import Path
from typing import Dict, List, Set

import structlog
from ruamel.yaml import YAML

ENGLISH_DOMAIN_FILENAME = "domain/domain.en.yml"
FRENCH_DOMAIN_FILENAME = "domain/domain.fr.yml"

RESPONSES_KEY = "responses"
BUTTONS_KEY = "buttons"
TEXT_KEY = "text"
TITLE_KEY = "title"
PAYLOAD_KEY = "payload"

CUSTOM_KEY = "custom"
DATA_KEY = "data"
DISABLE_TEXT_FIELD_KEY = "disableTextField"

log = structlog.get_logger()

RESPONSE_VARIANTS_EXCLUSIONS = {
    "utter_qa_sample_animal",
    "utter_qa_sample_contagion",
    "utter_qa_sample_resistance",
    "utter_qa_sample_cure",
    "utter_qa_sample_symptoms",
    "utter_qa_sample_spread",
    "utter_qa_sample_general",
    "utter_qa_sample_prevention",
    "utter_qa_sample_tests",
    "utter_qa_sample_walk",
    "utter_qa_sample_stats",
    "utter_test_navigation__display_titles",
    "utter_test_navigation__descriptions",
}


class ResponseVariantsNotSupported(Exception):
    def __init__(self, message):
        self.message = message


def get_text_elements(responses: Dict[str, List[dict]], response_id: str) -> Set[str]:
    response = responses[response_id]
    if len(response) != 1:
        raise ResponseVariantsNotSupported(
            f"Found response alternatives for response: {response_id}"
        )

    first_variant = response[0]
    text_elements = {first_variant[TEXT_KEY]}

    if BUTTONS_KEY in first_variant:
        text_elements |= {button[TITLE_KEY] for button in first_variant[BUTTONS_KEY]}

    return text_elements


def get_buttons(responses: Dict[str, List[dict]], response_id: str) -> List[str]:
    response = responses[response_id]
    if len(response) != 1:
        raise ResponseVariantsNotSupported(
            f"Found response alternatives for response: {response_id}"
        )

    first_variant = response[0]
    if BUTTONS_KEY in first_variant:
        return [button[PAYLOAD_KEY] for button in first_variant[BUTTONS_KEY]]

    return []


def disables_text(responses: Dict[str, List[dict]], response_id: str) -> str:
    response = responses[response_id]
    if len(response) != 1:
        raise ResponseVariantsNotSupported(
            f"Found response alternatives for response: {response_id}"
        )

    first_variant = response[0]

    return (
        first_variant.get(CUSTOM_KEY, {})
        .get(DATA_KEY, {})
        .get(DISABLE_TEXT_FIELD_KEY, "")
    )


def validate_response_ids(english_responses: dict, french_responses: dict) -> bool:
    english_response_ids = english_responses.keys()
    french_response_ids = french_responses.keys()

    if english_response_ids == french_response_ids:
        return False

    missing_english_response_ids = french_response_ids - english_response_ids
    missing_french_response_ids = english_response_ids - french_response_ids

    if missing_english_response_ids:
        log.error(
            "Missing english responses", response_ids=missing_english_response_ids
        )

    if missing_french_response_ids:
        log.error("Missing french responses", response_ids=missing_french_response_ids)

    return True


def validate_button_payloads(english_responses: dict, french_responses: dict) -> bool:
    button_mismatches = set()

    for response_id in english_responses.keys():
        if response_id not in french_responses:
            continue

        english_buttons = get_buttons(english_responses, response_id)
        french_buttons = get_buttons(french_responses, response_id)

        if english_buttons != french_buttons:
            button_mismatches.add(response_id)

    if button_mismatches:
        log.error("Button mismatches", response_ids=sorted(button_mismatches))

    return len(button_mismatches) != 0


def validate_translations(english_responses: dict, french_responses: dict) -> bool:
    missing_translations = set()

    for response_id in english_responses.keys():
        if response_id not in french_responses:
            continue

        english_text_elements = get_text_elements(english_responses, response_id)
        french_text_elements = get_text_elements(french_responses, response_id)

        if len(english_text_elements - french_text_elements) != len(
            english_text_elements
        ):
            missing_translations.add(response_id)

    if missing_translations:
        log.warn("Missing translations", response_ids=sorted(missing_translations))

    return len(missing_translations) != 0


def validate_text_field_disabled(
    english_responses: dict, french_responses: dict
) -> bool:
    text_disabled_mismatches = set()

    for response_id in english_responses.keys():
        if response_id not in french_responses:
            continue

        english_text_disabled = disables_text(english_responses, response_id)
        french_text_disabled = disables_text(french_responses, response_id)

        if english_text_disabled != french_text_disabled:
            text_disabled_mismatches.add(response_id)

    if text_disabled_mismatches:
        log.error(
            "Text field disabled inequally in responses",
            response_ids=sorted(text_disabled_mismatches),
        )

    return len(text_disabled_mismatches) != 0


def validate_domain() -> int:
    has_errors = False

    yaml = YAML(typ="safe")
    english = yaml.load(Path(ENGLISH_DOMAIN_FILENAME))
    french = yaml.load(Path(FRENCH_DOMAIN_FILENAME))

    english_responses = english[RESPONSES_KEY]
    french_responses = french[RESPONSES_KEY]

    has_errors |= validate_response_ids(english_responses, french_responses)

    # Removing response variants exclusions
    english_responses_without_alternatives = {
        key: value
        for key, value in english_responses.items()
        if key not in RESPONSE_VARIANTS_EXCLUSIONS
    }
    french_responses_without_alternatives = {
        key: value
        for key, value in french_responses.items()
        if key not in RESPONSE_VARIANTS_EXCLUSIONS
    }

    has_errors |= validate_button_payloads(
        english_responses_without_alternatives, french_responses_without_alternatives
    )

    has_errors |= validate_text_field_disabled(
        english_responses_without_alternatives, french_responses_without_alternatives
    )

    # Don't fail for missing translation
    validate_translations(
        english_responses_without_alternatives, french_responses_without_alternatives
    )

    if has_errors:
        return 1

    log.info("No error found in domain file.")
    return 0


if __name__ == "__main__":
    sys.exit(validate_domain())
