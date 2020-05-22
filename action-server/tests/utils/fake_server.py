from typing import Callable

from aiohttp import web
from aiohttp.test_utils import TestServer


class FakeServer:
    def __init__(self, route: str, create_response: Callable[[], web.Response]):
        self.app = web.Application()
        self.create_response = create_response
        self.app.router.add_routes([web.post(route, self.trigger_query)])
        self.server = TestServer(self.app)

    async def start(self):
        await self.server.start_server()
        return f"http://{self.server.host}:{self.server.port}"

    async def stop(self):
        await self.server.close()

    async def trigger_query(self, request):
        response = self.create_response()
        if isinstance(response, web.HTTPException):
            raise response
        return response
