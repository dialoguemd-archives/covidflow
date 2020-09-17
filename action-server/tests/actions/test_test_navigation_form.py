from typing import Any, Dict, List, Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from geopy.point import Point
from rasa_sdk.events import ActiveLoop, SlotSet
from rasa_sdk.forms import REQUESTED_SLOT

from covidflow.actions.test_navigation_form import (
    CLEARED_SLOTS,
    END_FORM_SLOT,
    FORM_NAME,
    INVALID_POSTAL_CODE_COUNTER_SLOT,
    LOCATIONS_SLOT,
    POSTAL_CODE_SLOT,
    TRY_DIFFERENT_ADDRESS_SLOT,
    TestNavigationForm,
    _generate_buttons,
    _generate_description,
    _locations_carousel,
)
from covidflow.utils.testing_locations import TestingLocation

from .form_test_helper import FormTestCase

BUTTON_TITLES = {
    "call_button": "Click to call: ",
    "directions_button": "Click to go",
    "website_button": "Click to visit",
}

DESCRIPTION_PARTS = {
    "contact_before_visit": "Contact me!",
    "referral": {
        "true": "referral = true",
        "false": "referral = false",
        "none": "referral = none",
    },
    "appointment_clientele": {
        "false": {
            "default": "no appointment default",
            "no_children_under": "no appointment no children {age}",
            "no_children_under_months": "no appointment no children {age} months",
            "known_clientele": "no appointment known clientele",
        },
        "true": {
            "default": "appointment default",
            "no_children_under": "appointment no children {age}",
            "no_children_under_months": "appointment no children {age} months",
            "known_clientele": "appointment known clientele",
        },
        "none": {
            "default": "appointment = none default",
            "no_children_under": "appointment = none no children {age}",
            "no_children_under_months": "appointment = none no children {age} months",
            "known_clientele": "appointment = none known clientele",
        },
    },
    "opening_hours": {
        "closed": "Closed",
        "time_format_short": "%-I%p",
        "time_format_long": "%-I:%M%p",
        "days": {
            "sunday": "Sun",
            "monday": "Mon",
            "tuesday": "Tue",
            "wednesday": "Wed",
            "thursday": "Thu",
            "friday": "Fri",
            "saturday": "Sat",
        },
    },
}

DOMAIN = {
    "responses": {
        "utter_test_navigation__display_titles": [{"custom": BUTTON_TITLES}],
        "utter_test_navigation__descriptions": [{"custom": DESCRIPTION_PARTS}],
        "utter_ask_test_navigation__try_different_address_error": [{"text": ""}],
    }
}

POSTAL_CODE = "H0H 0H0"
INVALID_POSTAL_CODE = "0H0 H0H"

USER_COORDINATES = Point([0.0, 0.0])
TESTING_LOCATION_RAW = {
    "id": "result",
    "name": "name",
    "_geoPoint": {"lon": -73.6662946, "lat": 45.4758369},
    "clientele": "Known Clientele",
    "requireReferral": True,
    "requireAppointment": True,
    "openingHours": {
        "monday": [
            {"start": "08:30:00", "end": "12:00:00"},
            {"start": "13:00:00", "end": "17:00:00"},
        ],
        "wednesday": [{"start": "08:00:00", "end": "16:00:00"}],
    },
}
TESTING_LOCATION = TestingLocation(TESTING_LOCATION_RAW)
TESTING_LOCATION_CARD_CONTENT = {
    "buttons": [
        {
            "title": "Click to go",
            "type": "web_url",
            "url": "http://maps.apple.com/?q=45.4758369,-73.6662946",
        }
    ],
    "image_url": "some_url",
    "subtitle": "8741.7km: appointment known clientele referral = true\n\n"
    + "Mon: 8:30am-12pm, 1pm-5pm\n"
    + "Tue: Closed\n"
    + "Wed: 8am-4pm\n"
    + "Thu: Closed\n"
    + "Fri: Closed\n"
    + "Sat: Closed\n"
    + "Sun: Closed",
    "title": "name",
}

SINGLE_CAROUSEL_CONTENT = {
    "type": "template",
    "payload": {
        "template_type": "generic",
        "elements": [TESTING_LOCATION_CARD_CONTENT],
    },
}

DOUBLE_CAROUSEL_CONTENT = {
    "type": "template",
    "payload": {
        "template_type": "generic",
        "elements": [TESTING_LOCATION_CARD_CONTENT, TESTING_LOCATION_CARD_CONTENT],
    },
}


def AsyncMock(*args, **kwargs):
    mock = MagicMock(*args, **kwargs)

    async def mock_coroutine(*args, **kwargs):
        return mock(*args, **kwargs)

    mock_coroutine.mock = mock
    return mock_coroutine


class TestTestNavigationForm(FormTestCase):
    def setUp(self):
        super().setUp()
        self.geocoding_patcher = patch(
            "covidflow.actions.test_navigation_form.Geocoding"
        )
        # Safeguard only, test using the mock should re-patch with AsyncMock
        self.testing_locations_patcher = patch(
            "covidflow.actions.test_navigation_form.get_testing_locations",
        )
        self.mock_geocoding = self.geocoding_patcher.start()
        self.testing_locations_patcher.start()
        self.form = TestNavigationForm()

    def tearDown(self):
        super().tearDown()
        self.geocoding_patcher.stop()
        self.testing_locations_patcher.stop()

    def _set_geocode(self, geocode=USER_COORDINATES, exception=False):
        if exception:
            self.mock_geocoding.return_value.get_from_postal_code.side_effect = (
                Exception
            )
        else:
            self.mock_geocoding.return_value.get_from_postal_code.return_value = geocode

    @pytest.mark.asyncio
    async def test_validate_postal_code(self):
        self._set_geocode()
        slot_mapping = self.form.slot_mappings()[POSTAL_CODE_SLOT]
        self.assertEqual(slot_mapping, self.form.from_text())

        await self._validate_postal_code("H0H 0H0", "H0H 0H0")
        await self._validate_postal_code("H0H0H0", "H0H0H0")
        await self._validate_postal_code("h0h 0h0", "h0h 0h0")
        await self._validate_postal_code("h0h0h0", "h0h0h0")
        await self._validate_postal_code("it's H0H 0H0!", "H0H 0H0")
        await self._validate_postal_code("it's h0h0h0", "h0h0h0")
        await self._validate_postal_code("0H0 H0H", None)
        await self._validate_postal_code("h0h 000", None)

    async def _validate_postal_code(self, text: str, expected_postal_code: str):
        tracker = self.create_tracker()
        slot_values = await self.form.validate_test_navigation__postal_code(
            text, self.dispatcher, tracker, None
        )

        self.assertEqual(expected_postal_code, slot_values.get(POSTAL_CODE_SLOT, None))

    def test_initialize(self):
        tracker = self.create_tracker(active_loop=False)

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [ActiveLoop(FORM_NAME), SlotSet(REQUESTED_SLOT, POSTAL_CODE_SLOT),]
        )

        self.assert_templates(["utter_ask_test_navigation__postal_code"])

    def test_postal_code_invalid_format(self):
        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=INVALID_POSTAL_CODE
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, None),
                SlotSet(INVALID_POSTAL_CODE_COUNTER_SLOT, 1),
                SlotSet(REQUESTED_SLOT, POSTAL_CODE_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_test_navigation__invalid_postal_code",
                "utter_ask_test_navigation__postal_code",
            ]
        )

    def test_postal_code_invalid_format_twice(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: POSTAL_CODE_SLOT,
                INVALID_POSTAL_CODE_COUNTER_SLOT: 1,
            },
            text=INVALID_POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, None),
                SlotSet(INVALID_POSTAL_CODE_COUNTER_SLOT, 2),
                SlotSet(REQUESTED_SLOT, POSTAL_CODE_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_test_navigation__invalid_postal_code",
                "utter_ask_test_navigation__postal_code",
            ]
        )

    def test_postal_code_invalid_format_thrice(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: POSTAL_CODE_SLOT,
                INVALID_POSTAL_CODE_COUNTER_SLOT: 2,
            },
            text=INVALID_POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(POSTAL_CODE_SLOT, None), SlotSet(END_FORM_SLOT, True),]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(["utter_test_navigation__invalid_postal_code_max"])

    def test_postal_code_geocoding_error(self):
        self._set_geocode(exception=True)

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=POSTAL_CODE
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(POSTAL_CODE_SLOT, POSTAL_CODE), SlotSet(END_FORM_SLOT, True),]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(
            [
                "utter_test_navigation__could_not_fetch_1",
                "utter_test_navigation__could_not_fetch_2",
            ]
        )

    def test_postal_code_nonexistent(self):
        self._set_geocode(None)

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=POSTAL_CODE
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, None),
                SlotSet(INVALID_POSTAL_CODE_COUNTER_SLOT, 1),
                SlotSet(REQUESTED_SLOT, POSTAL_CODE_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_test_navigation__invalid_postal_code",
                "utter_ask_test_navigation__postal_code",
            ]
        )

    def test_postal_code_nonexistent_twice(self):
        self._set_geocode(None)

        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: POSTAL_CODE_SLOT,
                INVALID_POSTAL_CODE_COUNTER_SLOT: 1,
            },
            text=POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, None),
                SlotSet(INVALID_POSTAL_CODE_COUNTER_SLOT, 2),
                SlotSet(REQUESTED_SLOT, POSTAL_CODE_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_test_navigation__invalid_postal_code",
                "utter_ask_test_navigation__postal_code",
            ]
        )

    def test_postal_code_nonexistent_thrice(self):
        self._set_geocode(None)

        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: POSTAL_CODE_SLOT,
                INVALID_POSTAL_CODE_COUNTER_SLOT: 2,
            },
            text=POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(POSTAL_CODE_SLOT, None), SlotSet(END_FORM_SLOT, True),]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(["utter_test_navigation__invalid_postal_code_max"])

    @patch(
        "covidflow.actions.test_navigation_form.get_testing_locations",
        new=AsyncMock(side_effect=Exception),
    )
    def test_postal_code_locations_error(self):
        self._set_geocode()

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=POSTAL_CODE
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(POSTAL_CODE_SLOT, POSTAL_CODE), SlotSet(END_FORM_SLOT, True),]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(
            [
                "utter_test_navigation__could_not_fetch_1",
                "utter_test_navigation__could_not_fetch_2",
            ]
        )

    @patch(
        "covidflow.actions.test_navigation_form.get_testing_locations",
        new=AsyncMock(return_value=[]),
    )
    def test_postal_code_no_results(self):
        self._set_geocode(USER_COORDINATES)

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, POSTAL_CODE),
                SlotSet(LOCATIONS_SLOT, []),
                SlotSet(REQUESTED_SLOT, TRY_DIFFERENT_ADDRESS_SLOT),
            ]
        )

        self.assert_templates(
            [
                "utter_test_navigation__no_locations",
                "utter_ask_test_navigation__try_different_address",
            ]
        )

    def test_try_different_address_affirm(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: TRY_DIFFERENT_ADDRESS_SLOT,
                POSTAL_CODE_SLOT: POSTAL_CODE,
                LOCATIONS_SLOT: [],
            },
            intent="affirm",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(TRY_DIFFERENT_ADDRESS_SLOT, True),
                SlotSet(POSTAL_CODE_SLOT, None),
                SlotSet(LOCATIONS_SLOT, None),
                SlotSet(REQUESTED_SLOT, POSTAL_CODE_SLOT),
            ]
        )

        self.assert_templates(["utter_ask_test_navigation__postal_code"])

    def test_try_different_address_deny(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: TRY_DIFFERENT_ADDRESS_SLOT,
                POSTAL_CODE_SLOT: POSTAL_CODE,
                LOCATIONS_SLOT: [],
            },
            intent="deny",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [SlotSet(TRY_DIFFERENT_ADDRESS_SLOT, False),]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(["utter_test_navigation__acknowledge"])

    def test_try_different_address_error(self):
        tracker = self.create_tracker(
            slots={
                REQUESTED_SLOT: TRY_DIFFERENT_ADDRESS_SLOT,
                POSTAL_CODE_SLOT: POSTAL_CODE,
                LOCATIONS_SLOT: [],
            },
            text="anything",
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(TRY_DIFFERENT_ADDRESS_SLOT, None),
                SlotSet(REQUESTED_SLOT, TRY_DIFFERENT_ADDRESS_SLOT),
            ]
        )

        self.assert_templates(
            ["utter_ask_test_navigation__try_different_address_error"]
        )

    @patch(
        "covidflow.actions.test_navigation_form.get_static_map_url",
        return_value="some_url",
    )
    @patch(
        "covidflow.actions.test_navigation_form.get_testing_locations",
        new=AsyncMock(return_value=[TESTING_LOCATION]),
    )
    def test_postal_code_one_result(self, mock_maps):
        self._set_geocode(USER_COORDINATES)

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, POSTAL_CODE),
                SlotSet(LOCATIONS_SLOT, [TESTING_LOCATION_RAW]),
            ]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(["utter_test_navigation__one_location", None])

        self.assert_attachments([None, SINGLE_CAROUSEL_CONTENT])

    @patch(
        "covidflow.actions.test_navigation_form.get_static_map_url",
        return_value="some_url",
    )
    @patch(
        "covidflow.actions.test_navigation_form.get_testing_locations",
        new=AsyncMock(return_value=[TESTING_LOCATION, TESTING_LOCATION]),
    )
    def test_postal_code_many_results(self, mock_maps):
        self._set_geocode(USER_COORDINATES)

        tracker = self.create_tracker(
            slots={REQUESTED_SLOT: POSTAL_CODE_SLOT}, text=POSTAL_CODE,
        )

        self.run_form(tracker, DOMAIN)

        self.assert_events(
            [
                SlotSet(POSTAL_CODE_SLOT, POSTAL_CODE),
                SlotSet(LOCATIONS_SLOT, [TESTING_LOCATION_RAW, TESTING_LOCATION_RAW]),
            ]
            + CLEARED_SLOTS
            + [ActiveLoop(None), SlotSet(REQUESTED_SLOT, None),]
        )

        self.assert_templates(
            [
                "utter_test_navigation__many_locations_1",
                "utter_test_navigation__many_locations_2",
                "utter_test_navigation__many_locations_3",
                None,
            ]
        )

        self.assert_attachments([None, None, None, DOUBLE_CAROUSEL_CONTENT])


class TestLocationsCarousel(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.patcher = patch(
            "covidflow.actions.test_navigation_form.get_static_map_url",
            return_value="some_url",
        )
        self.patcher.start()

    def tearDown(self):
        super().tearDown()
        self.patcher.stop()

    def _test_locations_carousel(self, raw_test_locations, cards_contents):
        test_locations = [TestingLocation(location) for location in raw_test_locations]
        self.assertEqual(
            _locations_carousel(test_locations, USER_COORDINATES, DOMAIN),
            {
                "type": "template",
                "payload": {"template_type": "generic", "elements": cards_contents},
            },
        )

    def test_carousel_one_location(self):

        self._test_locations_carousel(
            [TESTING_LOCATION_RAW], [TESTING_LOCATION_CARD_CONTENT]
        )

    def test_carousel_many_locations(self):
        location_2_raw = {
            "id": "result-2",
            "name": "name-2",
            "_geoPoint": {"lon": 2.0, "lat": 2.0},
        }
        card_2_content = {
            "buttons": [
                {
                    "title": "Click to go",
                    "type": "web_url",
                    "url": "http://maps.apple.com/?q=2.0,2.0",
                }
            ],
            "image_url": "some_url",
            "subtitle": "313.8km: appointment = none default referral = none Contact me!",
            "title": "name-2",
        }

        self._test_locations_carousel(
            [TESTING_LOCATION_RAW, location_2_raw],
            [TESTING_LOCATION_CARD_CONTENT, card_2_content],
        )

    def test_carousel_all_details(self):
        raw_location = {
            "id": "result",
            "name": "Test site name",
            "description": {
                "fr": "Test location described",
                "en": "serious description",
            },
            "address": {
                "country": "Canada",
                "unit": "200",
                "regionCode": "QC",
                "streetAddress": "5800 Cavendish Blvd",
                "countryCode": "CA",
                "postalCode": "H4W 2T5",
                "place": "Côte Saint-Luc",
                "region": None,
            },
            "_geoPoint": {"lon": 33.3333, "lat": 34.5678},
            "phones": [{"number": "5141112222", "extension": None, "type": "MAIN"}],
            "clientele": "Known Clientele",
            "requireReferral": True,
            "requireAppointment": True,
        }
        card_content = {
            "buttons": [
                {
                    "title": "Click to call: 514-111-2222",
                    "type": "web_url",
                    "url": "tel:514-111-2222",
                },
                {
                    "title": "Click to go",
                    "type": "web_url",
                    "url": "http://maps.apple.com/?q=5800+Cavendish+Blvd%2C+C%C3%B4te+Saint-Luc%2C+QC%2C+Canada",
                },
            ],
            "image_url": "some_url",
            "subtitle": "5164.5km: appointment known clientele referral = true",
            "title": "Test site name",
        }

        self._test_locations_carousel([raw_location], [card_content])

    def _test_buttons(self, buttons: List[Dict[str, Any]], **kwargs):
        raw_location = {
            "id": "result",
            "name": "Test site name",
            "description": {
                "fr": "Test location described",
                "en": "serious description",
            },
            "_geoPoint": {"lon": 0.0, "lat": 0.0},
            "phones": [],
            "websites": [],
        }
        raw_location.update(kwargs)

        test_location = TestingLocation(raw_location)
        self.assertEqual(_generate_buttons(test_location, BUTTON_TITLES), buttons)

    def test_generate_buttons_phone_with_extension(self):
        phones = [{"number": "5141112222", "extension": "3333", "type": "MAIN"}]
        expected_buttons = [
            {
                "title": "Click to call: 514-111-2222 ext. 3333",
                "type": "web_url",
                "url": "tel:514-111-2222",
            },
            {
                "title": "Click to go",
                "type": "web_url",
                "url": "http://maps.apple.com/?q=0.0,0.0",
            },
        ]

        self._test_buttons(expected_buttons, phones=phones)

    def test_generate_buttons_incomplete_address(self):
        address = {
            "country": "Canada",
            "regionCode": "QC",
            "place": "Côte Saint-Luc",
        }
        expected_buttons = [
            {
                "title": "Click to go",
                "type": "web_url",
                "url": "http://maps.apple.com/?q=0.0,0.0",
            },
        ]

        self._test_buttons(expected_buttons, address=address)

    def test_generate_buttons_no_phone_website(self):
        website = ("http://somewhereovertherainbow.com",)
        expected_buttons = [
            {"title": "Click to visit", "type": "web_url", "url": website,},
            {
                "title": "Click to go",
                "type": "web_url",
                "url": "http://maps.apple.com/?q=0.0,0.0",
            },
        ]

        self._test_buttons(expected_buttons, websites=[website])

    def test_generate_buttons_no_phone_no_website(self):
        expected_buttons = [
            {
                "title": "Click to go",
                "type": "web_url",
                "url": "http://maps.apple.com/?q=0.0,0.0",
            },
        ]

        self._test_buttons(expected_buttons)

    def _test_description(
        self,
        clientele: str,
        requireReferral: Optional[bool],
        requireAppointment: Optional[bool],
        description: str,
    ):
        raw_location = {
            "id": "result",
            "name": "Test site name",
            "description": {
                "fr": "Test location described",
                "en": "serious description",
            },
            "_geoPoint": {"lon": 0, "lat": 0},
            "phones": [],
            "clientele": clientele,
            "requireReferral": requireReferral,
            "requireAppointment": requireAppointment,
        }
        test_location = TestingLocation(raw_location)
        self.assertEqual(
            _generate_description(test_location, Point([0.0, 0.0]), DESCRIPTION_PARTS),
            description,
        )

    def test_description_no_referral_no_appointment_unknown_clientele(self):
        data = {
            "clientele": "Unknown",
            "requireReferral": False,
            "requireAppointment": False,
        }
        description = "0.0km: no appointment default referral = false Contact me!"

        self._test_description(description=description, **data)

    def test_description_referral_appointment_clientele_under_years(self):
        data = {
            "clientele": "No children under 13",
            "requireReferral": True,
            "requireAppointment": True,
        }
        description = "0.0km: appointment no children 13 referral = true"

        self._test_description(description=description, **data)

    def test_description_referral_no_appointment_clientele_under_months(self):
        data = {
            "clientele": "No children under 13 months",
            "requireReferral": True,
            "requireAppointment": False,
        }
        description = "0.0km: no appointment no children 13 months referral = true"

        self._test_description(description=description, **data)

    def test_description_referral_none(self):
        data = {
            "clientele": "known clientele",
            "requireReferral": None,
            "requireAppointment": True,
        }
        description = "0.0km: appointment known clientele referral = none Contact me!"

        self._test_description(description=description, **data)

    def test_description_appointment_none(self):
        data = {
            "clientele": "known clientele",
            "requireReferral": True,
            "requireAppointment": None,
        }
        description = (
            "0.0km: appointment = none known clientele referral = true Contact me!"
        )

        self._test_description(description=description, **data)
