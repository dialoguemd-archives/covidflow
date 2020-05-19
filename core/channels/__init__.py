from structlog.contextvars import bind_contextvars, clear_contextvars

from rasa.core.channels import SocketIOInput
from rasa.core.channels.channel import RestInput

from .setup_structlog import setup_structlog

setup_structlog()


def _create_on_new_message_wrapper(on_new_message):
    # This wrapper function binds sender_id to contextvars before calling the original function
    def on_new_message_wrapper(message):
        clear_contextvars()
        bind_contextvars(sender_id=message.sender_id)
        return on_new_message(message)

    return on_new_message_wrapper


class WrappedSocketIOInput(SocketIOInput):
    def blueprint(self, on_new_message):
        on_new_message_wrapper = _create_on_new_message_wrapper(on_new_message)
        return super().blueprint(on_new_message_wrapper)


class WrappedRestInput(RestInput):
    def blueprint(self, on_new_message):
        on_new_message_wrapper = _create_on_new_message_wrapper(on_new_message)
        return super().blueprint(on_new_message_wrapper)
