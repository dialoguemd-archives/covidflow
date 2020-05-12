from rasa_sdk import Tracker
from structlog.contextvars import bind_contextvars, clear_contextvars


def bind_logger(tracker: Tracker):
    clear_contextvars()
    bind_contextvars(sender_id=tracker.sender_id)
