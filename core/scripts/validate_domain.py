import sys
from pathlib import Path
from typing import List

from ruamel.yaml import YAML

ENGLISH_DOMAIN_FILENAME = "domain/domain.en.yml"
FRENCH_DOMAIN_FILENAME = "domain/domain.fr.yml"

RESPONSES_KEY = "responses"
BUTTONS_KEY = "buttons"
PAYLOAD_KEY = "payload"


def get_buttons(response: List[dict]) -> List[str]:
    if len(response) != 1:
        raise Exception("This tool does not support checking response variants (yet).")

    first_variant = response[0]
    if BUTTONS_KEY in first_variant:
        return [button[PAYLOAD_KEY] for button in first_variant[BUTTONS_KEY]]

    return []


def validate_domain() -> int:
    has_errors = False

    yaml = YAML(typ="safe")
    english = yaml.load(Path(ENGLISH_DOMAIN_FILENAME))
    french = yaml.load(Path(FRENCH_DOMAIN_FILENAME))

    english_responses = english[RESPONSES_KEY]
    french_responses = french[RESPONSES_KEY]

    english_response_ids = english_responses.keys()
    french_response_ids = french_responses.keys()

    if english_response_ids != french_response_ids:
        missing_english_response_ids = french_response_ids - english_response_ids
        missing_french_response_ids = english_response_ids - french_response_ids

        if missing_english_response_ids:
            print(f"Missing english responses: {missing_english_response_ids}")

        if missing_english_response_ids:
            print(f"Missing french responses: {missing_french_response_ids}")

        has_errors = True

    button_mismatches = set()

    for response_id in english_response_ids:
        if response_id not in french_responses:
            continue

        english_response = english_responses[response_id]
        french_response = french_responses[response_id]

        if get_buttons(english_response) != get_buttons(french_response):
            button_mismatches.add(response_id)

    if button_mismatches:
        print(f"Responses with button mismatches: {button_mismatches}")
        has_errors = True

    if has_errors:
        return 1

    print("No error found in domain file.")
    return 0


if __name__ == "__main__":
    sys.exit(validate_domain())
