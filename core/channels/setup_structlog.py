import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import pytz
import structlog
from pythonjsonlogger import jsonlogger
from structlog.contextvars import merge_contextvars

IS_STRUCTLOG_KEY = "is_structlog"

###
### FIXME: This file is a duplicate of "action-server/covidflow/setup_structlog.py".
###


def setup_structlog(
    *, level: Optional[str] = None, log_style: Optional[str] = None,
):
    """Configure structlog.

    Args:
        level (str): log level; If `None`, gets from `LOG_LEVEL` environment variable and
            falls back to `"DEBUG"`.
        log_style: Defines log output style. For now only 2 are supported: `json` and
            `pretty`; If `None`, gets from `LOG_STYLE` environment variable. Falls
            back to `"pretty"` if run from a terminal (if `sys.stdout.isatty() == True`);
    """
    environ: dict = lower_case_keys(os.environ)  # type: ignore
    if level is None:
        level = environ.get("log_level", "INFO")

    if log_style is None:
        default = "pretty" if sys.stdout.isatty() else "json"
        log_style = environ.get("log_style", default)

    if not logging.root.handlers:
        handler = logging.StreamHandler()
        logging.root.handlers.append(handler)

    if log_style == "pretty":
        processors = [
            merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(),
            _add_structlog_indicator,
        ]

    elif log_style == "json":
        processors = [
            merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
            _add_structlog_indicator,
        ]
        for handler in logging.root.handlers:  # type: ignore
            handler.setFormatter(CustomJsonFormatter())

    else:
        raise NotImplementedError(f"LOG_STYLE='{log_style}' is not implemented!")

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.root.setLevel(level)  # type: ignore


def _add_structlog_indicator(logger, name, log_event):
    log_event["extra"][IS_STRUCTLOG_KEY] = True
    return log_event


def _add_record(log_record: Dict[str, Any], key: str, value: Any):
    if not log_record.get(key):
        log_record[key] = value


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        if log_record.get(IS_STRUCTLOG_KEY) is True:
            del log_record[IS_STRUCTLOG_KEY]
        else:
            # Applying contextvars to non-structlog events
            contextvars = merge_contextvars(None, None, {})
            log_record.update(contextvars)

        timestamp = datetime.fromtimestamp(record.created, tz=pytz.utc)
        _add_record(log_record, "timestamp", timestamp.isoformat())
        _add_record(
            log_record,
            "timestamps",
            {
                "epoch": record.created,
                "utc": timestamp.isoformat(),
                "montreal": timestamp.astimezone(
                    pytz.timezone("America/Montreal")
                ).isoformat(),
            },
        )
        _add_record(log_record, "level", record.levelname.lower())
        _add_record(log_record, "lineno", record.lineno)
        _add_record(log_record, "pathname", record.pathname)
        _add_record(log_record, "threadName", record.threadName)
        _add_record(log_record, "processName", record.processName)


def lower_case_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k.lower(): v for k, v in d.items()}
