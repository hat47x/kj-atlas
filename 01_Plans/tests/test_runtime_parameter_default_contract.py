from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "docs_contract_checks.py"
SPEC = importlib.util.spec_from_file_location("docs_contract_checks", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RuntimeParameterDefaultContractTests(unittest.TestCase):
    def _write_fixture(self, root: Path, registry_default: str = "50,000") -> None:
        registry = root / "02_Architecture/runtime_parameter_registry.md"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            "# Runtime Parameter Registry\n\n"
            "### Profile default vs recommendation（既定値と推奨値）\n\n"
            "| Key | Implementation default | Enterprise recommendation | Rationale |\n"
            "| --- | --- | --- | --- |\n"
            f"| `KJ_ATLAS_MAX_DOCUMENT_CARDS` | `{registry_default}` | any | test |\n"
            "| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | required | test |\n"
            "| `KJ_ATLAS_LLM_PROVIDER` | `none` | none | test |\n",
            encoding="utf-8",
        )
        settings = root / "03_Implement/backend/src/kj_atlas_api/settings.py"
        settings.parent.mkdir(parents=True)
        settings.write_text(
            "class Settings:\n"
            "    max_document_cards: int = Field(default=50_000, ge=1)\n"
            "    admin_api_key: str | None = Field(default=None)\n"
            "    llm_provider: str = Field(default='none')\n"
            "    computed: int = Field(default_factory=lambda: 1)\n",
            encoding="utf-8",
        )

    def test_current_literal_defaults_match_after_numeric_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            self.assertEqual(MODULE.check_runtime_parameter_default_values(root), [])

    def test_registry_default_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root, registry_default="10,000")
            findings = MODULE.check_runtime_parameter_default_values(root)
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, MODULE.RUNTIME_PARAMETER_DEFAULT_RULE_ID)
        self.assertEqual(finding.target, "KJ_ATLAS_MAX_DOCUMENT_CARDS")
        self.assertIn("10000", finding.message)
        self.assertIn("50000", finding.message)

    def test_unset_and_none_string_remain_distinct_and_match_their_literals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            documented = MODULE._extract_profile_implementation_defaults(
                (root / "02_Architecture/runtime_parameter_registry.md").read_text(encoding="utf-8")
            )
        self.assertIsNone(documented["KJ_ATLAS_ADMIN_API_KEY"][0])
        self.assertEqual(documented["KJ_ATLAS_LLM_PROVIDER"][0], "none")

    def test_computed_defaults_are_outside_static_contract(self) -> None:
        settings = "class Settings:\n    value: int = Field(default_factory=lambda: 1)\n"
        self.assertEqual(MODULE._extract_settings_literal_defaults(settings), {})


if __name__ == "__main__":
    unittest.main()
