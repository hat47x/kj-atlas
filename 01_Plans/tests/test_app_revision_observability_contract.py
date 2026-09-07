from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_SETTINGS = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
BACKEND_OBSERVABILITY = ROOT / "03_Implement/backend/src/kj_atlas_api/observability.py"
FRONTEND_DIAGNOSTICS = ROOT / "03_Implement/frontend/src/export/diagnostics_bundle.ts"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"

EXPECTED_PATTERN = r"^[A-Za-z0-9._-]{1,64}$"


def _public_row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one public row for {key} in {path}, got {len(rows)}")
    return rows[0]


class AppRevisionObservabilityContractTests(unittest.TestCase):
    def test_backend_and_frontend_share_the_same_canonical_revision_pattern(self) -> None:
        backend = BACKEND_SETTINGS.read_text(encoding="utf-8")
        frontend = FRONTEND_DIAGNOSTICS.read_text(encoding="utf-8")

        backend_match = re.search(
            r'_APP_REVISION_PATTERN\s*=\s*re\.compile\(r"([^"]+)"\)',
            backend,
        )
        frontend_match = re.search(
            r"APP_REVISION_PATTERN\s*=\s*/([^/]+)/;",
            frontend,
        )

        self.assertIsNotNone(backend_match, "backend canonical revision pattern is missing")
        self.assertIsNotNone(frontend_match, "frontend canonical revision pattern is missing")
        self.assertEqual(backend_match.group(1), EXPECTED_PATTERN)
        self.assertEqual(frontend_match.group(1), EXPECTED_PATTERN)

    def test_runtime_registry_states_the_canonical_revision_boundary(self) -> None:
        registry = REGISTRY.read_text(encoding="utf-8")
        revision_rows = [
            line
            for line in registry.splitlines()
            if line.startswith("| `KJ_ATLAS_APP_REVISION` |")
        ]
        self.assertEqual(len(revision_rows), 1)
        row = revision_rows[0]
        self.assertIn("1〜64", row)
        self.assertIn("A-Za-z0-9._-", row)
        self.assertIn("`unknown`", row)

    def test_revision_is_exposed_in_json_and_human_readable_application_logs(self) -> None:
        observability = BACKEND_OBSERVABILITY.read_text(encoding="utf-8")
        self.assertIn(
            'payload["appRevision"] = getattr(record, "appRevision", "unknown") or "unknown"',
            observability,
        )
        self.assertIn("[rev=%(appRevision)s]", observability)

        for path in (REGISTRY, CONFIGURATION):
            row = _public_row(path, "KJ_ATLAS_APP_REVISION")
            self.assertIn("全アプリケーションログ", row)
            self.assertNotIn("構造化ログ", row)


if __name__ == "__main__":
    unittest.main()
