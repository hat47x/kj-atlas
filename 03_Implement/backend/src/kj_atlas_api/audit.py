from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal, Protocol
from urllib import error, request
from uuid import uuid4

from pydantic import BaseModel, Field

from kj_atlas_api.settings import settings
from kj_atlas_api.trusted_http import open_trusted_http

logger = logging.getLogger(__name__)

AuditEventType = Literal["view", "export", "query", "bundle", "proposal", "apply"]


class AuditEvent(BaseModel):
    schemaVersion: Literal[1] = 1
    eventId: str
    occurredAt: str
    eventType: AuditEventType
    docId: str
    safeMode: bool
    actorRefHash: str | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class AuditTransport(Protocol):
    name: str

    def send(self, event: AuditEvent) -> None:
        ...


class NoopAuditTransport:
    name = "noop"

    def send(self, event: AuditEvent) -> None:  # noqa: ARG002
        return


class HttpAuditTransport:
    name = "http"

    def __init__(self, endpoint: str, api_key: str | None = None, timeout_seconds: float = 2.0):
        self._endpoint = endpoint
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def send(self, event: AuditEvent) -> None:
        payload = event.model_dump_json().encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        req_obj = request.Request(
            self._endpoint,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with open_trusted_http(req_obj, timeout_seconds=self._timeout_seconds):
                return
        except error.HTTPError as exc:
            raise RuntimeError(f"audit transport failed with status {exc.code}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"audit transport failed: {exc.reason}") from exc




CE4_AUDIT_SCHEMA_VERSION = "ce4.audit.v1"
CE4_AUDIT_REQUIRED_FIELDS: tuple[str, ...] = (
    "operation",
    "safeMode",
    "equivalenceKey",
    "bundleHash",
    "sourceBundleHash",
    "queryHash",
    "dryRun",
    "sideEffect",
    "rejectReasonCode",
    "command",
    "channel",
    "schemaVersion",
)


def normalize_ce4_audit_metadata(raw: dict[str, object]) -> dict[str, object]:
    """Return CE4 audit metadata with the stable contract fields only."""
    normalized: dict[str, object] = {}
    for key in CE4_AUDIT_REQUIRED_FIELDS:
        normalized[key] = raw.get(key)
    normalized["schemaVersion"] = CE4_AUDIT_SCHEMA_VERSION
    return normalized
SENSITIVE_KEYS = {
    "text",
    "content",
    "prompt",
    "email",
    "name",
    "token",
    "secret",
    "authorization",
    "cookie",
}


def resolve_ce4_query_hash(metadata: dict[str, object]) -> str | None:
    """Return CE4 query hash in canonical priority order."""
    canonical = metadata.get("queryCanonicalHash")
    if isinstance(canonical, str) and canonical:
        return canonical
    legacy = metadata.get("queryHash")
    if isinstance(legacy, str) and legacy:
        return legacy
    return None


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mask_value(value: object) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return "[REDACTED]"


def sanitize_metadata(raw: dict[str, object]) -> dict[str, str | int | float | bool | None]:
    sanitized: dict[str, str | int | float | bool | None] = {}
    for key, value in raw.items():
        if key.lower() in SENSITIVE_KEYS:
            sanitized[key] = "[REDACTED]"
            continue
        sanitized[key] = _mask_value(value)
    return sanitized


def build_event(
    *,
    event_type: AuditEventType,
    doc_id: str,
    safe_mode: bool,
    actor_ref: str | None = None,
    metadata: dict[str, object] | None = None,
) -> AuditEvent:
    actor_ref_hash: str | None = None
    if actor_ref:
        actor_ref_hash = sha256(actor_ref.encode("utf-8")).hexdigest()[:24]

    return AuditEvent(
        eventId=f"audit-{uuid4()}",
        occurredAt=_now_utc_iso(),
        eventType=event_type,
        docId=doc_id,
        safeMode=safe_mode,
        actorRefHash=actor_ref_hash,
        metadata=sanitize_metadata(metadata or {}),
    )


@dataclass
class AuditDispatchResult:
    sent: bool
    reason: str | None = None


class AuditDispatcher:
    """Fail-open dispatcher.

    方針:
    - 無効化時: 完全no-op（副作用ゼロ）
    - 送信失敗時: 本体処理は継続（fail-open）
    - 失敗イベントはメモリ内キューへ退避し、次回送信時にbest-effortでflush
    - キュー上限超過時は最古イベントをdrop
    """

    def __init__(
        self,
        *,
        enabled: bool,
        allow_in_safe_mode: bool,
        transport: AuditTransport,
        queue_size: int,
    ):
        self._enabled = enabled
        self._allow_in_safe_mode = allow_in_safe_mode
        self._transport = transport
        self._queue: deque[AuditEvent] = deque(maxlen=max(queue_size, 0))

    @property
    def enabled(self) -> bool:
        return self._enabled

    def emit(self, event: AuditEvent) -> AuditDispatchResult:
        if not self._enabled:
            return AuditDispatchResult(sent=False, reason="disabled")

        if event.safeMode and not self._allow_in_safe_mode:
            return AuditDispatchResult(sent=False, reason="safe_mode_blocked")

        if self._queue:
            self._flush_queue()

        try:
            self._transport.send(event)
        except Exception as exc:  # fail-open
            self._enqueue(event)
            logger.warning(
                "audit event send failed; keep fail-open",
                extra={
                    "eventType": event.eventType,
                    "docId": event.docId,
                    "transport": self._transport.name,
                    "queueLength": len(self._queue),
                    "error": str(exc),
                },
            )
            return AuditDispatchResult(sent=False, reason="send_failed")

        return AuditDispatchResult(sent=True)

    def _flush_queue(self) -> None:
        pending = list(self._queue)
        self._queue.clear()
        for queued in pending:
            try:
                self._transport.send(queued)
            except Exception:
                self._enqueue(queued)
                break

    def _enqueue(self, event: AuditEvent) -> None:
        before = len(self._queue)
        self._queue.append(event)
        after = len(self._queue)
        dropped = before == after and after > 0
        if dropped:
            logger.warning(
                "audit queue is full; dropped oldest event",
                extra={"queueSize": after, "eventType": event.eventType, "docId": event.docId},
            )


def build_audit_dispatcher() -> AuditDispatcher:
    enabled = settings.audit_export_enabled
    allow_in_safe_mode = settings.audit_allow_in_safe_mode
    queue_size = settings.audit_queue_size

    if not enabled:
        return AuditDispatcher(
            enabled=False,
            allow_in_safe_mode=allow_in_safe_mode,
            transport=NoopAuditTransport(),
            queue_size=queue_size,
        )

    if settings.audit_transport == "http":
        endpoint = settings.audit_http_endpoint
        if not endpoint:
            logger.warning("KJ_ATLAS_AUDIT_TRANSPORT=http but KJ_ATLAS_AUDIT_HTTP_ENDPOINT missing; fallback noop")
            transport: AuditTransport = NoopAuditTransport()
        else:
            transport = HttpAuditTransport(
                endpoint=endpoint,
                api_key=settings.audit_http_api_key,
                timeout_seconds=settings.audit_http_timeout_seconds,
            )
    else:
        transport = NoopAuditTransport()

    return AuditDispatcher(
        enabled=enabled,
        allow_in_safe_mode=allow_in_safe_mode,
        transport=transport,
        queue_size=queue_size,
    )


def event_to_log_fields(event: AuditEvent) -> dict[str, object]:
    return json.loads(event.model_dump_json())
