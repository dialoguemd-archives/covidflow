import logging
from typing import Awaitable, Callable

from sanic import Blueprint
from structlog.contextvars import bind_contextvars, clear_contextvars

from rasa.core.channels.channel import RestInput, UserMessage
from rasa.core.channels.socketio import SocketIOInput

from .setup_structlog import setup_structlog

setup_structlog()
# hiding these logs since we don't want to see them
logging.getLogger("rasa.core.channels.socketio").setLevel(logging.INFO)


class ContextLog:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        bind_contextvars(*self.args, **self.kwargs)

    def __exit__(self, execution_type, execution_value, traceback):
        clear_contextvars()


def _create_on_new_message_wrapper(
    on_new_message: Callable[[UserMessage], Awaitable[None]]
) -> Callable[[UserMessage], Awaitable[None]]:
    # This wrapper function binds sender_id to contextvars before calling the original function
    def on_new_message_wrapper(message: UserMessage) -> UserMessage:
        with ContextLog(sender_id=message.sender_id):
            return on_new_message(message)

    return on_new_message_wrapper


class WrappedSocketIOInput(SocketIOInput):
    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        on_new_message_wrapper = _create_on_new_message_wrapper(on_new_message)
        return super().blueprint(on_new_message_wrapper)


class WrappedRestInput(RestInput):
    def blueprint(self, on_new_message: Callable[[UserMessage], Awaitable[None]]):
        on_new_message_wrapper = _create_on_new_message_wrapper(on_new_message)
        return super().blueprint(on_new_message_wrapper)
