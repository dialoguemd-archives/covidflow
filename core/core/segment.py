import logging
import os
from typing import Any, Dict, Optional, Text

import analytics
import structlog
from rasa.core.brokers.broker import EventBroker
from rasa.utils.endpoints import EndpointConfig

logger = structlog.get_logger()

SEGMENT_URL_DEFAULT = "https://api.segment.io"


def on_segment_error(error, items):
    logger.warning("segment_tracking_failed", error=error, items=items)


class SegmentSource(EventBroker):
    """ Track events with Segment"""

    def __init__(self, write_key: Optional[str] = None):

        if write_key is None:
            write_key = os.environ.get("SEGMENT_WRITE_KEY")

        if write_key is None:
            raise ValueError(
                "Failed to create segment source. Specify a 'SEGMENT_WRITE_KEY' environment variable or set the 'write_key' property in the event broker config endpoints.yml"
            )

        logging.getLogger("segment").setLevel(logging.INFO)
        analytics.host = os.environ.get("SEGMENT_URL", SEGMENT_URL_DEFAULT)
        analytics.write_key = write_key
        analytics.on_error = on_segment_error

    @classmethod
    def from_endpoint_config(cls, broker_config: EndpointConfig) -> "EventBroker":
        if broker_config is None:
            return None
        return cls(**broker_config.kwargs)

    def publish(self, event: Dict[Text, Any]) -> None:
        sender_id = event.pop("sender_id", None)
        event_name = event.pop("event", None)
        if sender_id and event_name:
            if event_name == "bot":
                # removing the metadata because it sends all of the slots to Segment
                # event sending only non-NULL slots would eventually create 1000s of columns
                event.pop("metadata", None)
            analytics.track(
                user_id=sender_id,
                event=event_name,
                properties=event,
                context={
                    # TODO: update this once a versioning strategy is established
                    "app": {"name": "covidflow", "version": "0.0.0", "build": "0"}
                },
            )
        else:
            logger.error("segment_tracking_failed_invalid_event", rasa_event=event)
