import asyncio
from unittest import TestCase
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestServer, unused_port

from covidflow.db.reminder import Reminder
from covidflow.jobs.send_reminders import (
    CORE_ENDPOINTS,
    EN,
    FR,
    HASHIDS_MIN_LENGTH_ENV_KEY,
    HASHIDS_SALT_ENV_KEY,
    _send_reminder,
    run,
)

HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4

REMINDER_1 = Reminder(
    id=1,
    timezone="America/Toronto",
    attributes={"first_name": "James", "phone_number": "15145551234", "language": FR},
)

REMINDER_2 = Reminder(
    id=2,
    timezone="America/Toronto",
    attributes={"first_name": "Lilly", "phone_number": "15145554567", "language": EN},
)


class TestJobSendReminder(TestCase):
    def _setUp(
        self,
        mock_session_factory,
        reminders=[REMINDER_1, REMINDER_2],
        fail_request=False,
        start_server=True,
    ):
        loop = asyncio.get_event_loop()
        self.server = {
            EN: FakeCoreServer(fail_request),
            FR: FakeCoreServer(fail_request),
        }

        self.core_endpoints = {
            EN: loop.run_until_complete(self.server[EN].start())
            if start_server
            else f"http://127.0.0.1:{unused_port()}",
            FR: loop.run_until_complete(self.server[FR].start())
            if start_server
            else f"http://127.0.0.1:{unused_port()}",
        }

        mock_session_factory.return_value.query.return_value.filter.return_value.all.return_value = (
            reminders
        )

    def tearDown(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.server[EN].stop())
            loop.run_until_complete(self.server[FR].stop())
        except AttributeError:
            pass

    def test_missing_environment_variables(self):
        with self.assertRaises(expected_exception=Exception):
            run()

    @patch("covidflow.jobs.send_reminders.session_factory")
    def test_with_environment_variables(self, mock_session_factory):
        self._setUp(mock_session_factory)

        with patch.dict(
            "os.environ",
            {
                HASHIDS_SALT_ENV_KEY: HASHIDS_SALT,
                HASHIDS_MIN_LENGTH_ENV_KEY: str(HASHIDS_MIN_LENGTH),
                CORE_ENDPOINTS[EN]: self.core_endpoints[EN],
                CORE_ENDPOINTS[FR]: self.core_endpoints[FR],
            },
        ):
            sent, errored = run()

        self.assertCountEqual(sent, [REMINDER_1.id, REMINDER_2.id])
        self.assertCountEqual(errored, [])

    @patch("covidflow.jobs.send_reminders.session_factory")
    def test_send_reminders(self, mock_session_factory):
        self._setUp(mock_session_factory)

        sent, errored = run(
            hashids_salt=HASHIDS_SALT,
            hashids_min_length=HASHIDS_MIN_LENGTH,
            core_endpoints=self.core_endpoints,
        )

        self.assertCountEqual(sent, [REMINDER_1.id, REMINDER_2.id])
        self.assertCountEqual(errored, [])

    @patch(
        "covidflow.jobs.send_reminders._send_reminder_with_backoff", side_effect=_send_reminder
    )
    @patch("covidflow.jobs.send_reminders.session_factory")
    def test_send_reminders_error(
        self, mock_session_factory, mock_send_reminder_with_backoff
    ):
        self._setUp(mock_session_factory, fail_request=True)

        sent, errored = run(
            hashids_salt=HASHIDS_SALT,
            hashids_min_length=HASHIDS_MIN_LENGTH,
            core_endpoints=self.core_endpoints,
        )

        self.assertCountEqual(sent, [])
        self.assertCountEqual(errored, [REMINDER_1.id, REMINDER_2.id])

    @patch("covidflow.jobs.send_reminders.session_factory")
    def test_send_no_reminders(self, mock_session_factory):
        self._setUp(mock_session_factory, reminders=[])

        sent, errored = run(
            hashids_salt=HASHIDS_SALT,
            hashids_min_length=HASHIDS_MIN_LENGTH,
            core_endpoints=self.core_endpoints,
        )

        self.assertCountEqual(sent, [])
        self.assertCountEqual(errored, [])

    @patch(
        "covidflow.jobs.send_reminders._send_reminder_with_backoff", side_effect=_send_reminder
    )
    @patch("covidflow.jobs.send_reminders.session_factory")
    def test_connection_error(
        self, mock_session_factory, mock_send_reminder_with_backoff
    ):
        self._setUp(mock_session_factory, start_server=False)

        sent, errored = run(
            hashids_salt=HASHIDS_SALT,
            hashids_min_length=HASHIDS_MIN_LENGTH,
            core_endpoints=self.core_endpoints,
        )

        self.assertCountEqual(sent, [])
        self.assertCountEqual(errored, [REMINDER_1.id, REMINDER_2.id])


class FakeCoreServer:
    route = "/conversations/{phone_number}/trigger_intent"

    def __init__(self, fail):
        self.app = web.Application()
        if fail:
            self.app.router.add_routes([web.post(self.route, self.trigger_intent_fail)])
        else:
            self.app.router.add_routes([web.post(self.route, self.trigger_intent)])
        self.server = TestServer(self.app)

    async def start(self):
        await self.server.start_server()
        return f"http://{self.server.host}:{self.server.port}"

    async def stop(self):
        await self.server.close()

    async def trigger_intent(self, request):
        return web.Response()

    async def trigger_intent_fail(self, request):
        raise web.HTTPBadRequest()
