from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
SAAS_POLICY = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"
KEY = "KJ_ATLAS_ALLOW_JIT_PROVISIONING"


def _table_row(section: str, key: str) -> list[str]:
    prefix = f"| `{key}` |"
    rows = [line for line in section.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return [cell.strip() for cell in rows[0].strip().strip("|").split("|")]


class JitProfileRecommendationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")

    def test_enterprise_recommendation_is_fail_closed(self) -> None:
        section = self.registry.split(
            "### Profile default vs recommendation（既定値と推奨値）", 1
        )[1].split("## Profile selection criteria", 1)[0]
        row = _table_row(section, KEY)
        self.assertEqual(row[1], "`false`")
        self.assertEqual(row[2], "`false`")
        self.assertIn("`local-dev` / `evaluation`", row[3])
        self.assertIn("本番は `false` 固定推奨", row[3])

    def test_local_dev_keeps_jit_conditional_not_required(self) -> None:
        profiles = self.registry.split("## Runtime profiles", 1)[1].split(
            "### Profile default vs recommendation", 1
        )[0]
        local_dev = next(
            line for line in profiles.splitlines() if line.startswith("| `local-dev` |")
        )
        cells = [cell.strip() for cell in local_dev.strip().strip("|").split("|")]
        self.assertNotIn(KEY, cells[2])
        self.assertIn("`KJ_ATLAS_ALLOW_JIT_PROVISIONING=true`", cells[3])
        self.assertIn("場合だけ", cells[3])

    def test_production_profiles_and_saas_runtime_require_jit_disabled(self) -> None:
        profiles = self.registry.split("## Runtime profiles", 1)[1].split(
            "### Profile default vs recommendation", 1
        )[0]
        enterprise = next(
            line for line in profiles.splitlines() if line.startswith("| `enterprise-production` |")
        )
        saas = next(
            line for line in profiles.splitlines() if line.startswith("| `saas-multitenant` |")
        )
        for row in (enterprise, saas):
            self.assertIn("`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`", row)

        policy = SAAS_POLICY.read_text(encoding="utf-8")
        self.assertIn(
            '(not self.allow_jit_provisioning, "disabled JIT provisioning")',
            policy,
        )


if __name__ == "__main__":
    unittest.main()
