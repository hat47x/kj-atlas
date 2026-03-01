from __future__ import annotations

from kj_atlas_api.audit import (
    AuditDispatcher,
    AuditEvent,
    build_event,
    sanitize_metadata,
)


class RecordingTransport:
    name = "recording"

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def send(self, event: AuditEvent) -> None:
        self.events.append(event)


class FailingTransport:
    name = "failing"

    def __init__(self) -> None:
        self.calls = 0

    def send(self, event: AuditEvent) -> None:  # noqa: ARG002
        self.calls += 1
        raise RuntimeError("boom")


def test_build_event_has_minimum_common_schema() -> None:
    event = build_event(
        event_type="view",
        doc_id="doc-1",
        safe_mode=True,
        actor_ref="alice@example.com",
        metadata={"route": "/docs/doc-1", "method": "GET"},
    )

    assert event.schemaVersion == 1
    assert event.eventType == "view"
    assert event.docId == "doc-1"
    assert event.safeMode is True
    assert event.actorRefHash is not None
    assert len(event.actorRefHash) == 24


def test_sanitize_metadata_masks_sensitive_keys() -> None:
    sanitized = sanitize_metadata(
        {
            "route": "/docs/doc-1",
            "email": "alice@example.com",
            "token": "secret-token",
            "nested": {"unsafe": True},
        }
    )

    assert sanitized["route"] == "/docs/doc-1"
    assert sanitized["email"] == "[REDACTED]"
    assert sanitized["token"] == "[REDACTED]"
    assert sanitized["nested"] == "[REDACTED]"


def test_dispatcher_off_is_side_effect_free() -> None:
    transport = RecordingTransport()
    dispatcher = AuditDispatcher(
        enabled=False,
        allow_in_safe_mode=False,
        transport=transport,
        queue_size=10,
    )
    event = build_event(event_type="view", doc_id="doc-1", safe_mode=True)

    result = dispatcher.emit(event)

    assert result.sent is False
    assert result.reason == "disabled"
    assert transport.events == []


def test_dispatcher_fail_open_on_transport_failure() -> None:
    dispatcher = AuditDispatcher(
        enabled=True,
        allow_in_safe_mode=True,
        transport=FailingTransport(),
        queue_size=2,
    )
    event = build_event(event_type="export", doc_id="doc-2", safe_mode=False)

    result = dispatcher.emit(event)

    assert result.sent is False
    assert result.reason == "send_failed"
