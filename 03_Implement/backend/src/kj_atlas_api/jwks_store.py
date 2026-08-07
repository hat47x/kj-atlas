"""ADR-0063 D2/D4/D5: JWKS key store with bounded caching.

Caching behavior (per identity_provider_id):
- Normal TTL: 600 seconds.
- Unknown kid cooldown: 60 seconds before a forced refresh is allowed.
- Max stale after refresh failure: 1800 seconds (no indefinite).
- In-flight refresh limit: 1 per provider at a time.
- Stale keys only affect which signing keys are tried; exp/iss/aud/alg
  validation is never relaxed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock


JWKS_NORMAL_TTL_SECONDS = 600
JWKS_COOLDOWN_SECONDS = 60
JWKS_MAX_STALE_SECONDS = 1800


@dataclass
class _CachedKeySet:
    keys: list[dict[str, object]]
    fetched_at: float
    refreshed_at: float

    def age(self) -> float:
        return time.monotonic() - self.fetched_at

    def is_fresh(self) -> bool:
        return self.age() < JWKS_NORMAL_TTL_SECONDS

    def is_stale_but_usable(self) -> bool:
        return self.age() < JWKS_MAX_STALE_SECONDS


@dataclass
class JwksStore:
    """Thread-safe in-process JWKS cache keyed by identity_provider_id."""

    _entries: dict[str, _CachedKeySet] = field(default_factory=dict)
    _last_failure: dict[str, float] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def get(self, provider_id: str) -> list[dict[str, object]] | None:
        """Return the current cached key set or None if absent/stale-expired."""
        with self._lock:
            entry = self._entries.get(provider_id)
            if entry is None:
                return None
            if entry.is_stale_but_usable():
                return list(entry.keys)
            # Beyond max stale — evict.
            del self._entries[provider_id]
            return None

    def set(self, provider_id: str, keys: list[dict[str, object]]) -> None:
        """Store a freshly fetched key set."""
        now = time.monotonic()
        with self._lock:
            existing = self._entries.get(provider_id)
            refreshed_at = existing.refreshed_at if existing is not None else now
            self._entries[provider_id] = _CachedKeySet(
                keys=list(keys),
                fetched_at=now,
                refreshed_at=refreshed_at,
            )
            self._last_failure.pop(provider_id, None)

    def set_fresh_failure(self, provider_id: str) -> None:
        """Record that a refresh attempt failed, without evicting cached keys."""
        with self._lock:
            self._last_failure[provider_id] = time.monotonic()

    def can_force_refresh(self, provider_id: str) -> bool:
        """True when the cooldown has elapsed (or no prior failure exists)."""
        with self._lock:
            last = self._last_failure.get(provider_id)
            if last is None:
                return True
            return (time.monotonic() - last) >= JWKS_COOLDOWN_SECONDS

    def needs_refresh(self, provider_id: str) -> bool:
        """True when the cached entry is absent or past normal TTL."""
        with self._lock:
            entry = self._entries.get(provider_id)
            if entry is None:
                return True
            return not entry.is_fresh()

    def find_key(self, provider_id: str, kid: str) -> dict[str, object] | None:
        """Return the key matching the given kid, or None."""
        keys = self.get(provider_id)
        if keys is None:
            return None
        for key in keys:
            if key.get("kid") == kid:
                return dict(key)
        return None
