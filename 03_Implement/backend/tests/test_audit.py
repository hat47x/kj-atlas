from __future__ import annotations

import pytest

from kj_atlas_api.audit import (
    AuditDispatcher,
    AuditEvent,
    HttpAuditTransport,
    MAX_AUDIT_EVENT_BYTES,
    build_audit_dispatcher,
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
        tenant_id="tenant-a",
        doc_id="doc-1",
        safe_mode=True,
        actor_ref="alice@example.com",
        metadata={"route": "/docs/doc-1", "method": "GET"},
    )

    assert event.schemaVersion == 1
    assert event.eventType == "view"
    assert event.tenantId == "tenant-a"
    assert event.docId == "doc-1"
    assert event.safeMode is True
    assert event.actorRefHash is not None
    assert len(event.actorRefHash) == 24


@pytest.mark.parametrize("tenant_id", ["", " tenant-a", "tenant-a\n"])
def test_build_event_rejects_missing_or_noncanonical_tenant_id(tenant_id: str) -> None:
    with pytest.raises(ValueError):
        build_event(
            event_type="view",
            tenant_id=tenant_id,
            doc_id="doc-1",
            safe_mode=True,
        )


def test_sanitize_metadata_masks_sensitive_keys() -> None:
    sanitized = sanitize_metadata(
        {
            "route": "/docs/doc-1",
            "email": "alice@example.com",
            "token": "secret-token",
            "client_secret": "client-secret",
            "tenantId": "tenant-b",
            "nested": {"unsafe": True},
        }
    )

    assert sanitized["route"] == "/docs/doc-1"
    assert sanitized["email"] == "[REDACTED]"
    assert sanitized["token"] == "[REDACTED]"
    assert sanitized["client_secret"] == "[REDACTED]"
    assert "tenantId" not in sanitized
    assert sanitized["nested"] == "[REDACTED]"


def test_sanitize_metadata_bounds_keys_values_and_field_count() -> None:
    sanitized = sanitize_metadata(
        {
            "oversized": "x" * 1025,
            "nonfinite": float("inf"),
            "bad\nkey": "not retained",
            **{f"field{index}": index for index in range(40)},
        }
    )

    assert sanitized["oversized"] == "[TRUNCATED]"
    assert sanitized["nonfinite"] == "[REDACTED]"
    assert "bad\nkey" not in sanitized
    assert len(sanitized) == 32


def test_dispatcher_off_is_side_effect_free() -> None:
    transport = RecordingTransport()
    dispatcher = AuditDispatcher(
        enabled=False,
        allow_in_safe_mode=False,
        transport=transport,
        queue_size=10,
    )
    event = build_event(
        event_type="view",
        tenant_id="tenant-a",
        doc_id="doc-1",
        safe_mode=True,
    )

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
    event = build_event(
        event_type="export",
        tenant_id="tenant-a",
        doc_id="doc-2",
        safe_mode=False,
    )

    result = dispatcher.emit(event)

    assert result.sent is False
    assert result.reason == "send_failed"


def test_build_audit_dispatcher_http_rejects_missing_endpoint(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr("kj_atlas_api.audit.settings.audit_transport", "http")
    monkeypatch.setattr("kj_atlas_api.audit.settings.audit_http_endpoint", None)

    with pytest.raises(RuntimeError) as exc_info:
        build_audit_dispatcher()

    assert "KJ_ATLAS_AUDIT_HTTP_ENDPOINT" in str(exc_info.value)


def test_build_audit_dispatcher_http_uses_configured_transport(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    captured: dict[str, object] = {}

    def recording_http_transport(
        endpoint: str,
        api_key: str | None,
        timeout_seconds: float,
    ) -> RecordingTransport:
        captured.update(
            endpoint=endpoint,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        return RecordingTransport()

    monkeypatch.setattr("kj_atlas_api.audit.settings.audit_export_enabled", True)
    monkeypatch.setattr("kj_atlas_api.audit.settings.audit_transport", "http")
    monkeypatch.setattr(
        "kj_atlas_api.audit.settings.audit_http_endpoint",
        "https://audit.example.invalid/events",
    )
    monkeypatch.setattr("kj_atlas_api.audit.settings.audit_http_api_key", "test-key")
    monkeypatch.setattr("kj_atlas_api.audit.settings.audit_http_timeout_seconds", 1.5)
    monkeypatch.setattr("kj_atlas_api.audit.HttpAuditTransport", recording_http_transport)

    dispatcher = build_audit_dispatcher()

    assert dispatcher.enabled is True
    assert captured == {
        "endpoint": "https://audit.example.invalid/events",
        "api_key": "test-key",
        "timeout_seconds": 1.5,
    }


def test_dispatcher_logs_a_warning_when_queue_flush_itself_fails(caplog) -> None:  # type: ignore[no-untyped-def]
    dispatcher = AuditDispatcher(
        enabled=True,
        allow_in_safe_mode=True,
        transport=FailingTransport(),
        queue_size=2,
    )
    first_event = build_event(
        event_type="export",
        tenant_id="tenant-a",
        doc_id="doc-2",
        safe_mode=False,
    )
    second_event = build_event(
        event_type="view",
        tenant_id="tenant-a",
        doc_id="doc-3",
        safe_mode=False,
    )
    dispatcher.emit(first_event)
    caplog.clear()

    with caplog.at_level("WARNING", logger="kj_atlas_api.audit"):
        dispatcher.emit(second_event)

    flush_records = [
        record for record in caplog.records
        if record.getMessage() == "audit event flush failed; keep fail-open"
    ]
    assert len(flush_records) == 1
    assert flush_records[0].docId == "doc-2"
    assert flush_records[0].tenantId == "tenant-a"
    assert flush_records[0].transport == "failing"


def test_http_transport_rejects_oversized_serialized_event(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    event = build_event(
        event_type="view",
        tenant_id="tenant-a",
        doc_id="doc-1",
        safe_mode=True,
    )
    monkeypatch.setattr(
        AuditEvent,
        "model_dump_json",
        lambda self: "x" * (MAX_AUDIT_EVENT_BYTES + 1),
    )

    transport = HttpAuditTransport(endpoint="http://127.0.0.1:9000/audit")

    try:
        transport.send(event)
    except RuntimeError as exc:
        assert str(exc) == "audit event exceeds the outbound size limit"
    else:
        assert False, "Expected oversized audit event to be rejected"
