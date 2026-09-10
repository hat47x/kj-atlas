"""SEC-RATE-LIMIT-01: minimal in-process, per-client-IP fixed-window limiter.

The MCP transport already rate-limits every route at 60 req/min/IP
(http_server.ts, express-rate-limit in-memory). The backend had no equivalent;
this closes the asymmetry for the admin provisioning surface, which is the
write path most at risk (user / identity-provider provisioning). It is
intentionally in-process: the only supported deployment is a single-worker
uvicorn process (see the issue's note), and in-memory state matches the MCP
precedent. A distributed store can replace the backing dict later without
changing the dependency contract.

Thread-safe: the guarded routes are synchronous (threadpool), so access to the
window map is serialized with a lock.
"""

from __future__ import annotations

import threading
import time
from typing import Final

# Match the MCP transport's default (express-rate-limit windowMs=60_000, limit=60).
_RATE_LIMIT_WINDOW_SECONDS: Final = 60.0
_RATE_LIMIT_MAX_REQUESTS: Final = 60


class _FixedWindow:
    """One client's current window."""

    __slots__ = ("start", "count")

    def __init__(self, start: float) -> None:
        self.start = start
        self.count = 0


class InMemoryRateLimiter:
    def __init__(self, *, window_seconds: float = _RATE_LIMIT_WINDOW_SECONDS, max_requests: int = _RATE_LIMIT_MAX_REQUESTS) -> None:
        self._window_seconds = window_seconds
        self._max_requests = max_requests
        self._windows: dict[str, _FixedWindow] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        """Return True when the request is allowed, False when the limit is hit.

        A failed (rejected) request does NOT consume a slot beyond the first
        rejection, so a client that keeps hammering stays rejected until the
        window rolls over.
        """
        now = time.monotonic()
        with self._lock:
            window = self._windows.get(key)
            if window is None or now - window.start >= self._window_seconds:
                window = _FixedWindow(now)
                self._windows[key] = window
            window.count += 1
            return window.count <= self._max_requests

    def reset(self) -> None:
        """Clear all state (test helper)."""
        with self._lock:
            self._windows.clear()


# Module-level singleton shared by the dependency. Kept here (not app.state) so
# the limiter is importable by tests without constructing the app.
DEFAULT_RATE_LIMITER = InMemoryRateLimiter()


def client_ip(request) -> str:
    """Best-effort client IP for rate-limit keying.

    This admin surface is loopback-only in the shipped compose (DEPLOY-NET-01),
    so `request.client.host` is authoritative; we do NOT trust X-Forwarded-For
    here because the provisioning surface predates the trusted-proxy contract
    and a spoofed header would let a caller rotate keys to bypass the limiter.
    """
    client = getattr(request, "client", None)
    host = getattr(client, "host", None)
    return host or "unknown"
