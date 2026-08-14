"""Structured (JSON) logging substrate for kj-atlas (OPS-OBSERV-01).

The app attaches context as ``extra={...}`` on its ``logging`` calls (audit
dispatch failures, LLM generation metadata, request correlation). The default
logging formatter drops those extra keys, so operators saw bare messages like
``llm_generate`` or ``audit event send failed; keep fail-open`` with no way to
attribute them. This module ships a JSON formatter that renders every extra key
plus the request correlation ID, and a ``configure_logging`` entry point driven
by ``KJ_ATLAS_LOG_LEVEL``.
"""

from __future__ import annotations

import json
import logging
import logging.config
from contextvars import ContextVar

# OPS-OBSERV-01 AC-2: the request correlation ID, set by the request-ID
# middleware in main.py and rendered into every log record emitted while a
# request is in flight.
request_id_var: ContextVar[str | None] = ContextVar("kj_atlas_request_id", default=None)

#: Standard LogRecord attributes the formatter must not treat as `extra`.
_STANDARD_ATTRS = frozenset(
    {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "taskName",
        "message",
        "asctime",
    }
)


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line.

    Renders the record's message, level, logger, the in-flight request ID, and
    every ``extra`` key the application attached (``tenantId``, ``docId``,
    ``eventType``, ``queueLength``, ``trace_id``, ``error``, ...). Any value is
    coerced to a JSON-safe form rather than letting a non-serializable extra
    break the record.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        if request_id:
            payload["requestId"] = request_id
        for key, value in record.__dict__.items():
            if key in _STANDARD_ATTRS or key in payload:
                continue
            payload[key] = self._safe(value)
        return json.dumps(payload, ensure_ascii=False, default=str)

    @staticmethod
    def _safe(value: object) -> object:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)


def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter on the root logger.

    The level is normalized defensively (an invalid ``KJ_ATLAS_LOG_LEVEL`` must
    not crash startup); ``logging`` itself rejects unknown level names, so we
    fall back to INFO.
    """
    normalized = str(level).strip().upper()
    if normalized not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}:
        normalized = "INFO"
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"level": normalized, "handlers": ["console"]},
        }
    )
