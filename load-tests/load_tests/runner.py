import time
from typing import Any, List

from locust.events import request_success
from rasa_integration_testing.interaction import Interaction, InteractionLoader
from rasa_integration_testing.runner import ScenarioRunner
from rasa_integration_testing.scenario import Scenario, ScenarioFragmentLoader
from socketio import Client

from load_tests.constants import SESSION_ID_KEY

EVENT_BOT_UTTERED = "bot_uttered"
EVENT_USER_UTTERED = "user_uttered"


class LocustRunner(ScenarioRunner):
    def __init__(
        self,
        interaction_loader: InteractionLoader,
        scenario_fragment_loader: ScenarioFragmentLoader,
    ):
        self._interaction_loader = interaction_loader
        self._scenario_fragment_loader = scenario_fragment_loader

    def run(self, scenario: Scenario, client: Client) -> None:
        interactions: List[Interaction] = self._resolve_interactions(scenario)
        start_time = time.time()
        accumulated_messages = []

        @client.event
        def bot_uttered(data):
            response_time = int((time.time() - start_time) * 1000)  # epochs to ms
            accumulated_messages.append(data)

            if len(interactions) > 0:
                expected_bot = self._interaction_loader.render_bot_turn(
                    interactions[0].bot
                )
                if len(accumulated_messages) == len(expected_bot):
                    request_success.fire(
                        request_type="socketio received",
                        name=EVENT_BOT_UTTERED,
                        response_time=response_time,
                        response_length=len(str(data)),
                    )
                    accumulated_messages.clear()
                    user_uttered(interactions.pop(0))

            elif len(accumulated_messages) > 0:
                client.disconnect()

        def user_uttered(interaction: Interaction):
            start_time = time.time()
            user_input = {SESSION_ID_KEY: client.sid}
            user_input.update(
                self._interaction_loader.render_user_turn(interaction.user)
            )
            _post(user_input, client)

        if len(interactions) > 0:
            user_uttered(interactions[0])


def _post(data: Any, client: Client) -> None:
    client.emit(EVENT_USER_UTTERED, data)
