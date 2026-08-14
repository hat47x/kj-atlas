"""SAAS-TENANT-SESSION-BINDING-01 AC-1 (ADR-0074 decision 2): keyed hashing
for the opaque auth-session cookie value.

The raw cookie value must never be persisted (decision 2). This module holds
the one hashing primitive used both when a session is created (hash-then-
store) and when a presented cookie is resolved (hash-then-lookup), so both
call sites are guaranteed to agree on the scheme.
"""

from __future__ import annotations

import hashlib
import hmac


def derive_session_key_hash(raw_session_id: str, *, key: bytes) -> str:
    """Keyed HMAC-SHA256 of the raw opaque session id.

    Deliberately keyed (unlike audit.py's unkeyed sha256 actor-ref hash,
    which has no precedent for hashing a value an attacker could otherwise
    brute-force from a leaked hash if the scheme were unkeyed and the raw
    id's entropy were ever in question).
    """
    return hmac.new(key, raw_session_id.encode("utf-8"), hashlib.sha256).hexdigest()
