import os
import time
from pathlib import Path
from typing import List

from locust import Locust, TaskSet, between, task
from rasa_integration_testing.helper import generate_tracker_id_from_scenario_name
from rasa_integration_testing.interaction import InteractionLoader
from rasa_integration_testing.scenario import (
    Scenario,
    ScenarioFragmentLoader,
    load_scenarios,
)
from socketio import Client

from load_tests.constants import SESSION_ID_KEY
from load_tests.runner import LocustRunner

ENV_INTEGRATION_TEST_PATH = "INTEGRATION_TEST_PATH"
ENV_LOAD_TEST_TARGET_URL = "LOAD_TEST_TARGET_URL"
ENV_MINIMUM_WAIT_TIME = "MINIMUM_WAIT_TIME"
ENV_MAXIMUM_WAIT_TIME = "MAXIMUM_WAIT_TIME"
DEFAULT_MINIMUM_WAIT_TIME = 0
DEFAULT_MAXIMUM_WAIT_TIME = 5

SCENARIOS_GLOB = "*.yml"
SCENARIOS_FOLDER = "scenarios"
TEST_CONFIG_FILE = "config.ini"

folder_path = Path(os.environ[ENV_INTEGRATION_TEST_PATH])
scenarios_path = folder_path.joinpath(SCENARIOS_FOLDER)
scenarios: List[Scenario] = load_scenarios(scenarios_path, SCENARIOS_GLOB)

runner: LocustRunner = LocustRunner(
    InteractionLoader(folder_path), ScenarioFragmentLoader(folder_path)
)


def _create_scenario_task(scenario: Scenario):
    @task
    def _scenario_task(self) -> None:
        client = Client()
        client.connect(os.environ[ENV_LOAD_TEST_TARGET_URL])
        session_id = generate_tracker_id_from_scenario_name(time.time(), scenario.name)
        client.emit("session_request", {SESSION_ID_KEY: session_id})
        runner.run(scenario, client, session_id)

    return _scenario_task


class IntegrationTestingSet(TaskSet):
    tasks = [_create_scenario_task(scenario) for scenario in scenarios]


class User(Locust):
    task_set = IntegrationTestingSet
    wait_time = between(
        float(os.environ.get(ENV_MINIMUM_WAIT_TIME, DEFAULT_MINIMUM_WAIT_TIME)),
        float(os.environ.get(ENV_MAXIMUM_WAIT_TIME, DEFAULT_MAXIMUM_WAIT_TIME)),
    )
