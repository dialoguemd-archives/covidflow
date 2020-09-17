import pytest
from rasa_sdk.events import (
    ActionExecuted,
    BotUttered,
    FollowupAction,
    UserUtteranceReverted,
    UserUttered,
)

from covidflow.actions.action_default_fallback import ActionDefaultFallback
from covidflow.constants import ACTION_LISTEN_NAME, FALLBACK_INTENT

from .action_test_helper import ActionTestCase

USER_TEXT = "It's home from work we go"
LATEST_EVENTS = [
    BotUttered(
        text="Heigh ho, heigh ho", metadata={"template_name": "utter_dwarfs_song"}
    ),
    ActionExecuted(ACTION_LISTEN_NAME),
    UserUttered(USER_TEXT),
]


class ActionDefaultFallbackTest(ActionTestCase):
    def setUp(self):
        super().setUp()
        self.action = ActionDefaultFallback()

    @pytest.mark.asyncio
    async def test_in_form(self):
        tracker = self.create_tracker(active_loop=True, events=LATEST_EVENTS)

        await self.run_action(tracker)

        self.assert_events(
            [UserUtteranceReverted(), FollowupAction(ACTION_LISTEN_NAME)]
        )

        self.assert_templates(["utter_dwarfs_song_error"])

    @pytest.mark.asyncio
    async def test_already_fallback_intent(self):
        tracker = self.create_tracker(intent=FALLBACK_INTENT, events=LATEST_EVENTS)

        await self.run_action(tracker)

        self.assert_events(
            [UserUtteranceReverted(), FollowupAction(ACTION_LISTEN_NAME)]
        )

        self.assert_templates(["utter_dwarfs_song_error"])

    @pytest.mark.asyncio
    async def test_other_intent(self):
        tracker = self.create_tracker(intent="unrelated", events=LATEST_EVENTS)

        await self.run_action(tracker)

        self.assert_events(
            [
                UserUtteranceReverted(),
                ActionExecuted(ACTION_LISTEN_NAME),
                UserUttered(
                    USER_TEXT,
                    parse_data={
                        "text": USER_TEXT,
                        "intent": {"name": FALLBACK_INTENT, "confidence": 1.0},
                        "intent_ranking": [
                            {"name": FALLBACK_INTENT, "confidence": 1.0}
                        ],
                        "entities": [],
                    },
                ),
            ]
        )

        self.assert_templates([])
