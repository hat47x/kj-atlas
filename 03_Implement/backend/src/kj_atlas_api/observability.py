"""OPS-OBSERV-01: the runtime substrate every runbook already assumes.

`04_Documentation/operations.md` and `diagnostics.md` are unusually complete for
a project this size, but every procedure in them terminates in "read the logs" or
"check /api/healthz" -- and both of those were, mechanically, near-empty:

- No logging configuration existed anywhere (no `basicConfig`, no `dictConfig`, no
  `--log-config`, no log-level setting). `logging.Formatter`'s default format
  string does not render `extra` keys, so the eight call sites that pass
  structured payloads that way emitted a bare sentence and threw the payload
  away. The worst case was the audit dispatcher's own failure warning, which
  carries `tenantId` / `docId` / `queueLength` / `error` in `extra`: an operator
  saw "audit event send failed; keep fail-open" with no indication of *whose*
  event was lost.
- No request identifier was generated or propagated, so a user reporting "it
  broke at 14:32" could not be joined to any log line. `x-trace-id` existed but
  was inbound-only: read from the caller, forwarded to the PDP, never generated,
  never logged, never echoed.

This module supplies both. It deliberately does not add a metrics dependency --
that is a separate decision recorded in the issue's 論点 section.

A third piece, added later (OPS-OBSERV-01 残作業, decided 2026-08-26): a
one-way pseudo-identifier for the acting principal, attached to every log line
the same way `requestId` is. `04_Documentation/security.md` forbids raw
subject identifiers (`subject`, `external_tenant_ref`, ...) in application
logs; that policy is unchanged. What was missing was the same completion the
audit trail already has -- SEC-ADMIN-PLANE-03's `admin_audit_events` table
carries `actorRefHash`, a truncated SHA-256 of the resolved principal id, so an
operator can tell "the same actor did both of these things" without ever
seeing who that actor is. `compute_actor_ref_hash` below is that same
computation, shared so the admin-audit path and the general log path can't
drift into two different hashes for the same principal.
"""

from __future__ import annotations

import json
import logging
import logging.config
import uuid
from contextvars import ContextVar
from hashlib import sha256

#: Set per request by `RequestIdMiddleware` and read by the log filter. A
#: ContextVar rather than a header lookup so that any `logger.*` call anywhere in
#: the request's call stack is correlated without threading an id through every
#: signature.
request_id_var: ContextVar[str | None] = ContextVar("kj_atlas_request_id", default=None)

#: Set once a request's principal is resolved -- by whichever identity path
#: fired (single-tenant header resolver, SaaS trusted session, control-plane
#: subject) -- and read by the same log filter as `request_id_var`. Requests
#: where no path resolves a principal (health checks, unauthenticated
#: single-tenant requests) never call `bind_actor_ref_hash`, so this stays at
#: its default of `None` and the field is simply absent from those log lines.
actor_ref_hash_var: ContextVar[str | None] = ContextVar("kj_atlas_actor_ref_hash", default=None)

#: Matches the truncation `record_admin_plane_audit` (main.py) already uses for
#: the admin audit trail's `actorRefHash` -- kept as one constant so the two
#: call sites cannot silently diverge.
ACTOR_REF_HASH_LENGTH = 16


def compute_actor_ref_hash(principal_id: str | None) -> str | None:
    """One-way fingerprint of an already-resolved principal id.

    Same algorithm and truncation as the admin audit trail's `actorRefHash`
    (SEC-ADMIN-PLANE-03), described in ADR-0079 as a "照合用fingerprint": it
    lets an operator correlate log lines from the same actor without the log
    ever carrying a reversible subject identifier. `None`/empty input means
    "no principal resolved" and returns `None` rather than hashing an empty
    string, so "anonymous" is never mistaken for a real (if unlikely) hash
    collision.
    """
    if not principal_id:
        return None
    return sha256(principal_id.encode("utf-8")).hexdigest()[:ACTOR_REF_HASH_LENGTH]


def bind_actor_ref_hash(principal_id: str | None) -> None:
    """Record the acting principal's fingerprint for the rest of this request.

    Call this as soon as a request's principal is resolved -- from any of the
    identity-resolution paths, whichever one actually fires for a given
    request. `main.py`'s `assign_request_id` middleware resets this to `None`
    at the start of every request, so a later call here is what makes it
    non-null; a request where nothing calls this stays anonymous.
    """
    actor_ref_hash_var.set(compute_actor_ref_hash(principal_id))


#: Response header and accepted inbound header. `x-trace-id` is honoured for
#: continuity with the existing PDP payload field, which already carries a
#: caller-supplied trace id (`access_control.py`).
REQUEST_ID_HEADER = "X-Request-Id"
INBOUND_TRACE_HEADER = "x-trace-id"

#: LogRecord attributes present on every record. Anything else was supplied by
#: the caller via `extra=` and belongs in the structured output.
_STANDARD_RECORD_FIELDS = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
        "requestId",
        "actorRefHash",
    }
)

#: Keys that must never reach a log line even if a caller puts them in `extra`.
#: `04_Documentation/security.md` forbids credentials and raw subject identifiers
#: in application logs; this is a mechanical backstop for that policy, not a
#: replacement for it.
_REDACTED_FIELDS = frozenset(
    {
        "api_key",
        "apiKey",
        "admin_api_key",
        "adminApiKey",
        "authorization",
        "cookie",
        "password",
        "secret",
        "subject",
        "token",
        "external_tenant_ref",
        "externalTenantRef",
    }
)

_REDACTED_PLACEHOLDER = "[redacted]"


class RequestIdFilter(logging.Filter):
    """Attach the current request id and actor pseudo-identifier to every record.

    Applied as a filter rather than inside the formatter so that a future
    non-JSON formatter still gets both fields. `actorRefHash` is `None` for any
    record emitted outside a request that resolved a principal (health checks,
    unauthenticated single-tenant requests, background/startup code) -- that is
    the expected, common case, not an error.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.requestId = request_id_var.get()
        record.actorRefHash = actor_ref_hash_var.get()
        return True


class JsonLogFormatter(logging.Formatter):
    """Render one JSON object per line, including caller-supplied `extra` fields.

    The point of this class is the `extra` handling: the default formatter drops
    those keys silently, which is why `tenantId` and `docId` never appeared in
    any log line despite the code computing them.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "requestId", None)
        if request_id:
            payload["requestId"] = request_id

        actor_ref_hash = getattr(record, "actorRefHash", None)
        if actor_ref_hash:
            payload["actorRefHash"] = actor_ref_hash

        for key, value in record.__dict__.items():
            if key in _STANDARD_RECORD_FIELDS or key.startswith("_"):
                continue
            payload[key] = _REDACTED_PLACEHOLDER if key in _REDACTED_FIELDS else value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(*, level: str, json_format: bool) -> None:
    """Install the process-wide logging configuration.

    Uvicorn's own loggers are routed through the same handler so that access
    lines and application lines share one format and one request id.
    """
    normalized_level = level.strip().upper() or "INFO"
    if normalized_level not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
        normalized_level = "INFO"

    formatter: dict[str, object]
    if json_format:
        formatter = {"()": f"{__name__}.JsonLogFormatter"}
    else:
        formatter = {
            # Human-readable fallback. `requestId` and `actorRefHash` are
            # included so both correlation paths work even when JSON output is
            # turned off. Unlike the JSON formatter (which omits the key
            # entirely when there is no principal), %-formatting can't
            # conditionally drop a field, so an anonymous request reads
            # literally as "actor=None" here.
            "format": "%(asctime)s %(levelname)s %(name)s [%(requestId)s] [actor=%(actorRefHash)s] %(message)s"
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": f"{__name__}.RequestIdFilter"}},
            "formatters": {"default": formatter},
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                    "filters": ["request_id"],
                }
            },
            "root": {"handlers": ["default"], "level": normalized_level},
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": normalized_level, "propagate": False},
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": normalized_level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": normalized_level,
                    "propagate": False,
                },
            },
        }
    )


def new_request_id() -> str:
    return uuid.uuid4().hex


def resolve_inbound_request_id(raw: str | None) -> str | None:
    """Accept a caller-supplied trace id only if it is safe to echo and log.

    A caller-controlled value ends up in a response header and in log lines, so
    it is constrained to a short opaque token. Anything else is discarded in
    favour of a server-generated id rather than rejected, because a malformed
    trace header must not fail an otherwise valid request.
    """
    if raw is None:
        return None
    candidate = raw.strip()
    if not candidate or len(candidate) > 128:
        return None
    if not all(character.isalnum() or character in "-_" for character in candidate):
        return None
    return candidate
