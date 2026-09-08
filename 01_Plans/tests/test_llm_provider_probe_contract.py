from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
AI_ROUTE = ROOT / "03_Implement/backend/src/kj_atlas_api/routes/ai.py"
PROVIDER = ROOT / "03_Implement/backend/src/kj_atlas_api/llm/provider.py"
KEY = "KJ_ATLAS_LLM_PROVIDER"


def _backend_row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows: list[str] = []
    in_backend = False
    for line in text.splitlines():
        if line == "## Backend settings":
            in_backend = True
            continue
        if in_backend and line.startswith("## "):
            break
        if in_backend and line.startswith(prefix):
            rows.append(line)
    if len(rows) != 1:
        raise AssertionError(f"expected one backend row for {key}, got {len(rows)}")
    return rows[0]


class LlmProviderProbeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.ai_route = AI_ROUTE.read_text(encoding="utf-8")
        self.provider = PROVIDER.read_text(encoding="utf-8")

    def test_registry_uses_provider_status_instead_of_healthz_or_startup_log(self) -> None:
        row = _backend_row(self.registry, KEY)
        self.assertIn("GET /ai/provider-status", row)
        self.assertIn("providerKind", row)
        self.assertIn("canonical runtime kind", row)
        self.assertNotIn("起動ログまたは `/healthz`", row)

    def test_provider_status_reports_the_resolved_runtime_kind(self) -> None:
        self.assertIn('@router.get("/provider-status", response_model=ProviderStatusResponse)', self.ai_route)
        self.assertIn("providerKind=get_provider().provider_kind", self.ai_route)

    def test_documented_aliases_match_the_runtime_registry(self) -> None:
        row = _backend_row(self.registry, KEY)
        self.assertIn("`local_http`→`local`", row)
        self.assertIn("`large_scale`/`external`→`large-scale`", row)
        self.assertIn('registry.register("local", LocalProvider, aliases=("local_http",))', self.provider)
        self.assertIn('registry.register("large-scale", LargeScaleProvider, aliases=("large_scale", "external"))', self.provider)


if __name__ == "__main__":
    unittest.main()
