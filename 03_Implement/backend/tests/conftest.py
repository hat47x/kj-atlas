from __future__ import annotations

import os


# CI harness may export a generic DATABASE_URL for unrelated jobs.
# ENV-ARCH-01 enforces KJ_ATLAS_* only and rejects legacy keys at import-time,
# so we sanitize test process env before application modules are imported.
os.environ.pop("DATABASE_URL", None)
