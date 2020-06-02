import re
from datetime import time
from typing import Any, Dict, List, Optional, Text, Union

import structlog
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from covidflow.utils.geocoding import Geocoding
from covidflow.utils.maps import get_map_url
from covidflow.utils.testing_locations import (
    Day,
    OpeningHour,
    TestingLocation,
    TestingLocationPhone,
    get_testing_locations,
)

from .constants import LANGUAGE_SLOT, TEST_NAVIGATION_SUCCESS_SLOT
from .lib.log_util import bind_logger

logger = structlog.get_logger()

FORM_NAME = "test_navigation_form"


POSTAL_CODE_REGEX = re.compile(r"[a-z]\d[a-z] ?\d[a-z]\d", re.IGNORECASE)
MAX_POSTAL_CODE_TRIES = 2

POSTAL_CODE_SLOT = "test_navigation__postal_code"
INVALID_POSTAL_CODE_COUNTER_SLOT = "test_navigation__invalid_postal_code_counter"
TRY_DIFFERENT_ADDRESS_SLOT = "test_navigation__try_different_address"
LOCATIONS_SLOT = "test_navigation__locations"
END_FORM_SLOT = "test_navigation__end_form"

CHILDREN_CLIENTELE_REGEXP = re.compile(r"no_children_under_(\d{1,2})(_months)?")


class TestNavigationForm(FormAction):
    def __init__(self):
        self.geocoding_client = Geocoding()

        super().__init__()

    def name(self) -> Text:
        return FORM_NAME

    async def run(
        self, dispatcher, tracker, domain,
    ):
        bind_logger(tracker)
        return await super().run(dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        if tracker.get_slot(END_FORM_SLOT) is True:
            return []

        if tracker.get_slot(LOCATIONS_SLOT):
            return [POSTAL_CODE_SLOT]

        return [POSTAL_CODE_SLOT, TRY_DIFFERENT_ADDRESS_SLOT]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            POSTAL_CODE_SLOT: self.from_text(),
            TRY_DIFFERENT_ADDRESS_SLOT: [
                self.from_intent(intent="affirm", value=True),
                self.from_intent(intent="deny", value=False),
            ],
        }

    async def validate_test_navigation__postal_code(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        postal_code = _get_postal_code(value)
        if postal_code is None:
            return _check_postal_code_error_counter(tracker, dispatcher)

        try:
            coordinates = self.geocoding_client.get_from_postal_code(postal_code)
            if coordinates is None:
                return _check_postal_code_error_counter(tracker, dispatcher)

            testing_locations = await get_testing_locations(coordinates)

        except Exception:
            logger.exception("Failed to fetch testing locations")
            dispatcher.utter_message(
                template="utter_test_navigation__could_not_fetch_1"
            )
            dispatcher.utter_message(
                template="utter_test_navigation__could_not_fetch_2"
            )
            return {POSTAL_CODE_SLOT: postal_code, END_FORM_SLOT: True}

        if len(testing_locations) == 0:
            dispatcher.utter_message(template="utter_test_navigation__no_locations")

        elif len(testing_locations) == 1:
            dispatcher.utter_message(template="utter_test_navigation__one_location")
            dispatcher.utter_message(
                attachment=_locations_carousel(
                    tracker.get_slot(LANGUAGE_SLOT), domain, testing_locations
                )
            )

        else:
            dispatcher.utter_message(
                template="utter_test_navigation__many_locations_1",
                nb_testing_sites=len(testing_locations),
            )
            dispatcher.utter_message(template="utter_test_navigation__many_locations_2")
            dispatcher.utter_message(template="utter_test_navigation__many_locations_3")
            dispatcher.utter_message(
                attachment=_locations_carousel(
                    tracker.get_slot(LANGUAGE_SLOT), domain, testing_locations
                )
            )

        return {
            POSTAL_CODE_SLOT: postal_code,
            LOCATIONS_SLOT: [location.raw_data for location in testing_locations],
        }

    def validate_test_navigation__try_different_address(
        self,
        value: bool,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if value:
            return {POSTAL_CODE_SLOT: None, LOCATIONS_SLOT: None}

        dispatcher.utter_message(template="utter_test_navigation__acknowledge")
        return {}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        if tracker.get_slot(LOCATIONS_SLOT):
            success = True
        else:
            success = False

        return [SlotSet(TEST_NAVIGATION_SUCCESS_SLOT, success)]


def _get_postal_code(text: str) -> Optional[str]:
    matches = POSTAL_CODE_REGEX.search(text)
    if matches:
        return matches.group()
    return None


def _check_postal_code_error_counter(
    tracker: Tracker, dispatcher: CollectingDispatcher
) -> Dict[Text, Any]:
    try_counter = tracker.get_slot(INVALID_POSTAL_CODE_COUNTER_SLOT)

    if try_counter == MAX_POSTAL_CODE_TRIES:
        dispatcher.utter_message(
            template="utter_test_navigation__invalid_postal_code_max"
        )
        return {POSTAL_CODE_SLOT: None, END_FORM_SLOT: True}

    dispatcher.utter_message(template="utter_test_navigation__invalid_postal_code")

    return {
        POSTAL_CODE_SLOT: None,
        INVALID_POSTAL_CODE_COUNTER_SLOT: try_counter + 1,
    }


def _locations_carousel(
    language: str, domain: Dict[Text, Any], testing_locations: List[TestingLocation]
) -> Dict[Text, Any]:
    responses = domain.get("responses", {})
    titles_response = responses.get("utter_test_navigation__display_titles", [])

    titles = titles_response[0].get("custom", {}) if len(titles_response) >= 1 else {}

    descriptions_response = responses.get("utter_test_navigation__descriptions", [])
    description_parts = (
        descriptions_response[0].get("custom", {})
        if len(descriptions_response) >= 1
        else {}
    )

    cards = [
        _generate_location_card(location, titles, description_parts, language)
        for location in testing_locations
    ]
    return {
        "type": "template",
        "payload": {"template_type": "generic", "elements": cards},
    }


def _generate_location_card(
    location: TestingLocation,
    titles: Dict[Text, Text],
    description_parts: Dict[Text, Any],
    language: str,
) -> Dict[Text, Any]:
    phone_number = (
        _format_phone_number(location.phones[0]) if len(location.phones) >= 1 else None
    )
    buttons = (
        [
            _url_button(
                f"{titles.get('call_button')}{phone_number['full']}",
                f"tel:{phone_number['link']}",
            )
        ]
        if phone_number
        else []
    )
    buttons.append(
        _url_button(
            titles["directions_button"],
            f"http://maps.apple.com/?q={location.coordinates[0]},{location.coordinates[1]}",
        )
    )

    return {
        "title": location.name,
        "subtitle": _generate_description(location, description_parts),
        "image_url": get_map_url(location.coordinates),
        "buttons": buttons,
    }


def _format_phone_number(phone_number: TestingLocationPhone) -> Dict[Text, str]:
    number = phone_number.number[-10:]  # remove first number if country code is there
    formatted_number = f"{number[0:3]}-{number[3:6]}-{number[6:10]}"
    full_number = (
        f"{formatted_number} ext. {phone_number.extension}"
        if phone_number.extension
        else formatted_number
    )
    return {"full": full_number, "link": formatted_number}


def _url_button(title: str, url: str) -> Dict[Text, Any]:
    return {
        "title": title,
        "type": "web_url",
        "url": url,
    }


def _generate_description(
    location: TestingLocation, description_parts: Dict[Text, Any]
) -> str:
    require_referral = str(location.require_referral).lower()
    referral_part = description_parts.get("referral", {}).get(require_referral, "")

    require_appointment = str(location.require_appointment).lower()
    clientele = str(location.clientele).lower().replace(" ", "_")

    children_age_clientele = CHILDREN_CLIENTELE_REGEXP.fullmatch(clientele)
    age = None
    if children_age_clientele:
        age = children_age_clientele.group(1)
        if children_age_clientele.group(2):
            clientele = "no_children_under_months"
        else:
            clientele = "no_children_under"

    appointment_clientele_part = (
        description_parts.get("appointment_clientele", {})
        .get(require_appointment, {})
        .get(clientele)
    )

    unknown_clientele = False
    if appointment_clientele_part is None:
        logger.warn(f"Unknown clientele received from Clinia API: {location.clientele}")
        unknown_clientele = True
        appointment_clientele_part = (
            description_parts.get("appointment_clientele", {})
            .get(require_appointment, {})
            .get("default", "")
        )

    if age:
        appointment_clientele_part = appointment_clientele_part.replace("{age}", age)

    description = f"{appointment_clientele_part} {referral_part}"

    if (
        location.require_referral is None
        or location.require_appointment is None
        or unknown_clientele is True
    ):
        description += f" {description_parts.get('contact_before_visit', '')}"

    days_part: Dict[str, str] = description_parts["days"]
    if len(location.opening_hours) > 0:
        description += f"\n{_format_opening_hours(location.opening_hours, days_part)}"

    return description


def _format_hour(time: time):
    return time.strftime("%H") if time.minute == 0 else time.strftime("%H:%M")


def _format_hours(hours: List[OpeningHour]):
    if len(hours) == 0:
        return "-"
    return ", ".join(
        [f"{_format_hour(start)}-{_format_hour(end)}" for (start, end) in hours]
    )


def _format_opening_hours(
    opening_hours: Dict[Day, List[OpeningHour]], days_part: Dict[str, str]
):
    rendered_opening_hours = [
        f"{days_part[day.name]}: {_format_hours(opening_hours.get(day, []))}"
        for (day) in Day
    ]
    return "\n".join(rendered_opening_hours)
