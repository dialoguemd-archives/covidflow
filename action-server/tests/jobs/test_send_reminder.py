import asyncio
from unittest import TestCase
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import TestServer, unused_port

from db.reminder import Reminder
from jobs.send_reminders import _send_reminder, run

EN = "en"
FR = "fr"

HASHIDS_SALT = "abcd1234"
HASHIDS_MIN_LENGTH = 4

ENV = {
    "REMINDER_ID_HASHIDS_SALT": HASHIDS_SALT,
    "REMINDER_ID_HASHIDS_MIN_LENGTH": str(HASHIDS_MIN_LENGTH),
}

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
        self.server = dict()
        port = dict()

        self.server[EN] = FakeCoreServer(fail_request)
        self.server[FR] = FakeCoreServer(fail_request)

        if start_server:
            port[EN] = loop.run_until_complete(self.server[EN].start())
            port[FR] = loop.run_until_complete(self.server[FR].start())
        else:
            port[EN] = unused_port()
            port[FR] = unused_port()

        self.core_endpoints = {
            EN: f"127.0.0.1:{port[EN]}",
            FR: f"127.0.0.1:{port[FR]}",
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

    @patch.dict("os.environ", ENV)
    @patch("jobs.send_reminders.session_factory")
    def test_with_environment_variables(self, mock_session_factory):
        self._setUp(mock_session_factory)

        sent, errored = run(core_endpoints=self.core_endpoints)

        self.assertCountEqual(sent, [REMINDER_1.id, REMINDER_2.id])
        self.assertCountEqual(errored, [])

    @patch("jobs.send_reminders.session_factory")
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
        "jobs.send_reminders._send_reminder_with_backoff", side_effect=_send_reminder
    )
    @patch("jobs.send_reminders.session_factory")
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

    @patch("jobs.send_reminders.session_factory")
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
        "jobs.send_reminders._send_reminder_with_backoff", side_effect=_send_reminder
    )
    @patch("jobs.send_reminders.session_factory")
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
        return self.server.port

    async def stop(self):
        await self.server.close()

    async def trigger_intent(self, request):
        return web.Response()

    async def trigger_intent_fail(self, request):
        raise web.HTTPBadRequest()
