from __future__ import annotations

import json
import logging
from pathlib import Path

from kj_atlas_api.observability import JsonLogFormatter, RequestIdFilter, configure_logging


def _record() -> logging.LogRecord:
    return logging.LogRecord(
        name="kj_atlas_api.revision_test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="revision-test",
        args=(),
        exc_info=None,
    )


def test_json_log_contains_the_configured_app_revision() -> None:
    record = _record()
    RequestIdFilter(app_revision="rev-2026.09.06_1").filter(record)

    payload = json.loads(JsonLogFormatter().format(record))
    assert payload["appRevision"] == "rev-2026.09.06_1"


def test_human_readable_logging_keeps_the_revision_correlation_field() -> None:
    try:
        configure_logging(
            level="INFO",
            json_format=False,
            app_revision="rev-2026.09.06_1",
        )
        handler = logging.getLogger().handlers[0]
        assert "%(appRevision)s" in handler.formatter._fmt

        record = _record()
        for log_filter in handler.filters:
            log_filter.filter(record)
        assert record.appRevision == "rev-2026.09.06_1"
    finally:
        configure_logging(level="INFO", json_format=True, app_revision="unknown")


def test_main_wires_the_canonical_settings_revision_into_logging() -> None:
    main_path = Path(__file__).resolve().parents[1] / "src/kj_atlas_api/main.py"
    source = main_path.read_text(encoding="utf-8")
    assert "configure_logging(" in source
    assert "app_revision=settings.app_revision" in source
