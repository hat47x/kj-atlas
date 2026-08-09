"""ADR-0063 D9-2: unit tests for the JwksStore."""

from __future__ import annotations


from kj_atlas_api.jwks_store import (
    JwksStore,
)


_RSA_KEY = {
    "kty": "RSA",
    "kid": "key-1",
    "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAt",
    "e": "AQAB",
}


class TestJwksStore:
    def test_get_returns_none_when_empty(self) -> None:
        store = JwksStore()
        assert store.get("provider-1") is None

    def test_set_and_get_roundtrip(self) -> None:
        store = JwksStore()
        keys = [_RSA_KEY]
        store.set("provider-1", keys)
        assert store.get("provider-1") == keys

    def test_get_returns_copy_not_reference(self) -> None:
        store = JwksStore()
        keys = [_RSA_KEY]
        store.set("provider-1", keys)
        retrieved = store.get("provider-1")
        assert retrieved is not keys
        assert retrieved == keys

    def test_needs_refresh_when_empty(self) -> None:
        store = JwksStore()
        assert store.needs_refresh("provider-1") is True

    def test_needs_refresh_after_set_when_fresh(self) -> None:
        store = JwksStore()
        store.set("provider-1", [_RSA_KEY])
        # Immediately after set, should be fresh.
        assert store.needs_refresh("provider-1") is False

    def test_set_clears_failure_state(self) -> None:
        store = JwksStore()
        store.set_fresh_failure("provider-1")
        store.set("provider-1", [_RSA_KEY])
        assert store.can_force_refresh("provider-1") is True

    def test_find_key_returns_matching_kid(self) -> None:
        store = JwksStore()
        store.set("provider-1", [_RSA_KEY])
        found = store.find_key("provider-1", "key-1")
        assert found == _RSA_KEY

    def test_find_key_returns_none_for_unknown_kid(self) -> None:
        store = JwksStore()
        store.set("provider-1", [_RSA_KEY])
        assert store.find_key("provider-1", "unknown-kid") is None

    def test_find_key_returns_none_for_empty_store(self) -> None:
        store = JwksStore()
        assert store.find_key("provider-1", "key-1") is None

    def test_can_force_refresh_initially_true(self) -> None:
        store = JwksStore()
        assert store.can_force_refresh("provider-1") is True

    def test_can_force_refresh_false_after_failure(self) -> None:
        store = JwksStore()
        store.set_fresh_failure("provider-1")
        assert store.can_force_refresh("provider-1") is False

    def test_providers_are_independent(self) -> None:
        store = JwksStore()
        store.set("provider-1", [_RSA_KEY])
        store.set_fresh_failure("provider-2")
        assert store.get("provider-1") == [_RSA_KEY]
        assert store.can_force_refresh("provider-1") is True
        assert store.can_force_refresh("provider-2") is False
