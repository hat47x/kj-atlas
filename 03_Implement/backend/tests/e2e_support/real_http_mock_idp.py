"""Expose the existing Level 2 mock IdP with a real HTTP issuer for browser E2E."""

from __future__ import annotations

import os

from tests.level2 import mock_idp

mock_idp._MOCK_BASE = os.environ.get(
    "KJ_ATLAS_MOCK_IDP_BASE", "http://localhost:9100"
).rstrip("/")

app = mock_idp.app
