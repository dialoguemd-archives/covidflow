import sys
from pathlib import Path
from typing import List, Set

import structlog
from ruamel.yaml import YAML

ENGLISH_DOMAIN_FILENAME = "domain/domain.en.yml"
FRENCH_DOMAIN_FILENAME = "domain/domain.fr.yml"

RESPONSES_KEY = "responses"
BUTTONS_KEY = "buttons"
TEXT_KEY = "text"
TITLE_KEY = "title"
PAYLOAD_KEY = "payload"

log = structlog.get_logger()


class ResponseVariantsNotSupported(Exception):
    pass


def get_text_elements(response: List[dict]) -> Set[str]:
    if len(response) != 1:
        raise ResponseVariantsNotSupported()

    first_variant = response[0]

    text_elements = {first_variant[TEXT_KEY]}

    if BUTTONS_KEY in first_variant:
        text_elements |= {button[TITLE_KEY] for button in first_variant[BUTTONS_KEY]}

    return text_elements


def get_buttons(response: List[dict]) -> List[str]:
    if len(response) != 1:
        raise ResponseVariantsNotSupported()

    first_variant = response[0]
    if BUTTONS_KEY in first_variant:
        return [button[PAYLOAD_KEY] for button in first_variant[BUTTONS_KEY]]

    return []


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
    has_response_variants = set()

    for response_id in english_responses.keys():
        if response_id not in french_responses:
            continue

        english_response = english_responses[response_id]
        french_response = french_responses[response_id]

        try:
            if get_buttons(english_response) != get_buttons(french_response):
                button_mismatches.add(response_id)
        except ResponseVariantsNotSupported:
            has_response_variants.add(response_id)
            continue

    if has_response_variants:
        log.warn(
            "Your domain has response variants which are not supported by this tool.",
            response_ids=sorted(has_response_variants),
        )
    if button_mismatches:
        log.error("Button mismatches", response_ids=sorted(button_mismatches))

    return len(button_mismatches) != 0


def validate_translations(english_responses: dict, french_responses: dict) -> bool:
    missing_translations = set()
    has_response_variants = set()

    for response_id in english_responses.keys():
        if response_id not in french_responses:
            continue

        english_response = english_responses[response_id]
        french_response = french_responses[response_id]

        try:
            english_text_elements = get_text_elements(english_response)
            french_text_elements = get_text_elements(french_response)
        except ResponseVariantsNotSupported:
            has_response_variants.add(response_id)
            continue

        if len(english_text_elements - french_text_elements) != len(
            english_text_elements
        ):
            missing_translations.add(response_id)

    if has_response_variants:
        log.warn(
            "Your domain has response variants which are not supported by this tool.",
            response_ids=sorted(has_response_variants),
        )
    if missing_translations:
        log.warn("Missing translations", response_ids=sorted(missing_translations))

    return len(missing_translations) != 0


def validate_domain() -> int:
    has_errors = False

    yaml = YAML(typ="safe")
    english = yaml.load(Path(ENGLISH_DOMAIN_FILENAME))
    french = yaml.load(Path(FRENCH_DOMAIN_FILENAME))

    english_responses = english[RESPONSES_KEY]
    french_responses = french[RESPONSES_KEY]

    has_errors |= validate_response_ids(english_responses, french_responses)
    has_errors |= validate_button_payloads(english_responses, french_responses)

    # Don't fail for missing translation
    validate_translations(english_responses, french_responses)

    if has_errors:
        return 1

    log.info("No error found in domain file.")
    return 0


if __name__ == "__main__":
    sys.exit(validate_domain())
