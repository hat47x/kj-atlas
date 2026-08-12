"""SEC-RATE-LIMIT-01: unit tests for the in-process fixed-window limiter."""

from __future__ import annotations

from kj_atlas_api.rate_limit import InMemoryRateLimiter


def test_limiter_allows_up_to_max_requests_then_rejects() -> None:
    limiter = InMemoryRateLimiter(window_seconds=60.0, max_requests=3)

    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is False  # 4th exceeds the 3 limit

    # A different client has its own window.
    assert limiter.allow("client-b") is True


def test_limiter_keys_are_isolated_per_client() -> None:
    limiter = InMemoryRateLimiter(window_seconds=60.0, max_requests=1)

    assert limiter.allow("a") is True
    assert limiter.allow("a") is False
    assert limiter.allow("b") is True


def test_reset_clears_all_state() -> None:
    limiter = InMemoryRateLimiter(window_seconds=60.0, max_requests=1)

    assert limiter.allow("a") is True
    assert limiter.allow("a") is False
    limiter.reset()
    assert limiter.allow("a") is True
