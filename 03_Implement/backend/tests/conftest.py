"""Shared pytest fixtures for kj-atlas test suite.

Fixtures defined here are automatically available to all test modules
without explicit import (pytest conftest convention).
"""

from __future__ import annotations

import os

# CI harness may export a generic DATABASE_URL for unrelated jobs.
# ENV-ARCH-01 enforces KJ_ATLAS_* only and rejects legacy keys at import-time,
# so we sanitize test process env before application modules are imported.
os.environ.pop("DATABASE_URL", None)


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

TIMESTAMP = "2026-08-08T00:00:00Z"

# Minimal ASGI scope for creating fake Request objects in unit tests.
# The InMemoryActiveTenantSessionPersister methods accept Request but
# don't read from it — only principal_id is used.
FAKE_ASGI_SCOPE: dict = {"type": "http", "method": "GET", "path": "/"}


# ---------------------------------------------------------------------------
# Shared test doubles
# ---------------------------------------------------------------------------


class StubCapabilityResolver:
    """Minimal capability resolver for SaaS E2E tests.

    Returns a fixed snapshot with document.read + document.write.
    Used across multiple E2E test files.
    """

    def resolve(self, *, db, principal_id, tenant):
        from kj_atlas_api.session_context import CapabilitySnapshot

        return CapabilitySnapshot(
            effective_capabilities=("document.read", "document.write"),
            capability_version="stub-v1",
        )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def fake_request():
    """Create a minimal Starlette Request for unit tests."""
    from starlette.requests import Request

    return Request(scope=FAKE_ASGI_SCOPE)


def fake_response():
    """Create a minimal Starlette Response for unit tests."""
    from starlette.responses import Response

    return Response()
